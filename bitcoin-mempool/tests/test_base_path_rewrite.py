import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "containers" / "bitcoin-mempool" / "configure-mempool-base-path.sh"
NGINX_TEMPLATE_PATH = REPO_ROOT / "containers" / "bitcoin-mempool" / "nginx-mempool.conf"


class BasePathRewriteTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mempool-base-path-"))
        self.web_root = self.temp_dir / "web"
        (self.web_root / "en-US").mkdir(parents=True)
        (self.web_root / "resources").mkdir(parents=True)
        (self.web_root / "resources" / "favicons").mkdir(parents=True)
        self.template_path = self.temp_dir / "nginx.template.conf"
        self.output_path = self.temp_dir / "nginx.conf"
        shutil.copy2(NGINX_TEMPLATE_PATH, self.template_path)

        (self.web_root / "en-US" / "index.html").write_text(
            textwrap.dedent(
                """\
                <!doctype html>
                <html>
                <head>
                  <script src="/resources/config.js"></script>
                  <base href="/">
                  <link rel="manifest" href="/resources/favicons/site.webmanifest">
                </head>
                <body></body>
                </html>
                """
            ),
            encoding="utf-8",
        )
        (self.web_root / "main.js").write_text(
            textwrap.dedent(
                """\
                const api = "/api/v1/status";
                const docs = '/docs/faq';
                const resources = `/resources/logo.svg`;
                const css = "url(/resources/bg.png)";
                const network = "/testnet4";
                const enterprise = '/enterprise';
                const block = "/mempool-block/0";
                """
            ),
            encoding="utf-8",
        )
        (self.web_root / "resources" / "config.js").write_text(
            "(function (window) { window.__env = window.__env || {}; }((typeof global !== 'undefined') ? global : this));\n",
            encoding="utf-8",
        )
        (self.web_root / "resources" / "favicons" / "site.webmanifest").write_text(
            '{"src": "/resources/favicons/android-chrome-192x192.png"}\n',
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def run_script(self, base_path=None, expect_success=True):
        env = os.environ.copy()
        env.update(
            {
                "MEMPOOL_WEB_ROOT": str(self.web_root),
                "MEMPOOL_NGINX_TEMPLATE": str(self.template_path),
                "MEMPOOL_NGINX_OUTPUT": str(self.output_path),
                "MEMPOOL_BASE_PATH_STAMP": str(self.temp_dir / ".stamp"),
            }
        )
        if base_path is not None:
            env["MEMPOOL_BASE_PATH"] = base_path
        else:
            env.pop("MEMPOOL_BASE_PATH", None)

        result = subprocess.run(
            ["bash", str(SCRIPT_PATH)],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if expect_success:
            self.assertEqual(result.returncode, 0, msg=result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_rewrites_prefixed_deployment(self):
        self.run_script("/proxy/mempool")

        nginx = self.output_path.read_text(encoding="utf-8")
        index_html = (self.web_root / "en-US" / "index.html").read_text(encoding="utf-8")
        main_js = (self.web_root / "main.js").read_text(encoding="utf-8")
        config_js = (self.web_root / "resources" / "config.js").read_text(encoding="utf-8")
        manifest = (self.web_root / "resources" / "favicons" / "site.webmanifest").read_text(encoding="utf-8")

        self.assertIn("location /proxy/mempool/ {", nginx)
        self.assertIn("rewrite ^/proxy/mempool(/.*)$ $1 break;", nginx)
        self.assertIn("location = /proxy/mempool {", nginx)

        self.assertIn('<script src="/proxy/mempool/resources/config.js"></script>', index_html)
        self.assertIn('<base href="/proxy/mempool/', index_html)
        self.assertIn("/proxy/mempool/api/v1/status", main_js)
        self.assertIn("/proxy/mempool/docs/faq", main_js)
        self.assertIn("/proxy/mempool/resources/logo.svg", main_js)
        self.assertIn("url(/proxy/mempool/resources/bg.png)", main_js)
        self.assertIn("/proxy/mempool/testnet4", main_js)
        self.assertIn("/proxy/mempool/enterprise", main_js)
        self.assertIn("/proxy/mempool/mempool-block/0", main_js)
        self.assertIn("/proxy/mempool/resources/favicons/android-chrome-192x192.png", manifest)
        self.assertIn("window.__env.BASE_PATH = '/proxy/mempool';", config_js)

    def test_defaults_to_root_when_env_is_unset(self):
        self.run_script()

        nginx = self.output_path.read_text(encoding="utf-8")
        index_html = (self.web_root / "en-US" / "index.html").read_text(encoding="utf-8")
        main_js = (self.web_root / "main.js").read_text(encoding="utf-8")
        config_js = (self.web_root / "resources" / "config.js").read_text(encoding="utf-8")

        self.assertIn("location / {", nginx)
        self.assertNotIn("location =  {", nginx)
        self.assertIn('<base href="/">', index_html)
        self.assertIn('"/api/v1/status"', main_js)
        self.assertIn("`/resources/logo.svg`", main_js)
        self.assertIn("window.__env.BASE_PATH = '/';", config_js)

    def test_refuses_to_rewrite_existing_files_for_different_prefix(self):
        self.run_script("/one")
        result = self.run_script("/two", expect_success=False)
        self.assertIn("start a fresh container to change it", result.stderr)

    def test_patch_keeps_browser_api_base_url_relative(self):
        patch_text = (REPO_ROOT / "containers" / "bitcoin-mempool" / "mempool-basepath.patch").read_text(
            encoding="utf-8"
        )

        self.assertIn("+    this.apiBaseUrl = '';", patch_text)
        self.assertNotIn(
            "+    this.apiBaseUrl = this.stateService.env.BASE_PATH === '/' ? '' : this.stateService.env.BASE_PATH;",
            patch_text,
        )
        self.assertNotIn(
            "+    let apiBaseUrl = this.stateService.env.BASE_PATH === '/' ? '' : this.stateService.env.BASE_PATH;",
            patch_text,
        )
        self.assertIn("+      const basePath = this.stateService.env.BASE_PATH === '/' ? '' : this.stateService.env.BASE_PATH;", patch_text)


if __name__ == "__main__":
    unittest.main()
