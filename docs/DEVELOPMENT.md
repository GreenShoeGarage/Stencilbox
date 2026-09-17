# Developer guide

## Runtime versus developer requirements

End users open `index.html`; no installation or build is needed. Development verification uses Node.js 22 and Python 3.13 as specified by `.nvmrc` and `.python-version`. Python dependencies in `requirements-dev.txt` are **only test tools**. The app has no npm dependencies and does not need `npm install`.

```sh
# Verify the checked-in single-file app matches source
python3 build.py --check
python3 tools/check_repo.py

# Rebuild after editing src/
python3 build.py

# Pure Node.js geometry tests; no packages needed
node tests/geometry.test.js
# npm test is an equivalent convenience command
```

On Windows, `py -3` may be used instead of `python3`. Run commands from the repository root unless a script is invoked by absolute path.

## Independent geometry and browser tests

A virtual environment keeps the development tools separate:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 tests/validate_stl.py
python3 -m playwright install chromium
python3 tests/browser.test.py
```

On Windows activate with `.venv\Scripts\Activate.ps1`. Linux CI installs browser system dependencies with `python3 -m playwright install --with-deps chromium`.

The browser runner uses `CHROMIUM_EXECUTABLE` when set, then a `chromium` on PATH, otherwise Playwright's installed browser. It tests the packaged HTML with an isolated DOM, controlled storage, and intercepted export payloads. It does not require a server or navigate to remote sites. Read the exact limitations in [TESTING.md](TESTING.md).

## Outputs do not dirty the repository

Fresh test results are written to ignored `artifacts/test-results/`. The files under `tests/*-results.json` remain the original release evidence, not the output of each local run. `STENCILBOX_TEST_OUTPUT` overrides the fresh results directory.

The geometry suite writes new sample exports into `artifacts/test-results/examples/`, leaving the reviewed `examples/` files untouched. The independent validator checks `examples/` by default. Set `STENCILBOX_EXAMPLES` to test another complete set of eight studies. CI verifies both the checked-in examples and the newly generated exports.

`python3 tests/smoke.py` produces screenshots in `artifacts/screenshots/`; set `STENCILBOX_SCREENSHOT_OUTPUT` to choose another directory. Review generated images before deliberately replacing the README's checked-in screenshots. This smoke script prints diagnostics; the asserting browser suite is the CI gate.

## Prepare another distribution

```sh
python3 tools/package_release.py
```

The packager first verifies the committed HTML matches source, then creates `dist/stencilbox-v1.0.0-repo.zip`, a standalone HTML copy, and `dist/SHA256SUMS.txt`. The version comes from `VERSION`. The ZIP has one top-level `stencilbox/` folder, retains hidden configuration files, and excludes `.git`, private environment files, caches, virtual environments, and generated artifacts. Members are sorted and use a fixed timestamp for repeatable packaging of identical inputs.

The packaging script is not a replacement for running tests. It does not initialize Git, create a remote repository, sign a release, or publish anything.

## Repository automation

`ci.yml` verifies the portable build, repository structure, JavaScript syntax, 224 geometry cases, independent STL geometry, browser interactions, and release packaging. It also checks that tests leave tracked files unchanged. It runs on pushes, pull requests, and manual requests and can be called by the Pages workflow.

`pages.yml` is manual by default and calls CI before deployment. It uses the checked-in `index.html`; a build is not required to serve the app. See [deployment details](DEPLOYMENT.md).

GitHub Actions and pip Dependabot checks are monthly. These affect developer infrastructure, not runtime networking. Review upgrades and rerun tests. Action major tags are used for maintainability; organizations requiring immutable pins may replace them with reviewed full commit SHAs.

## Rename compatibility regressions

Run `node tests/rename.test.js` for all eight original JSON fixtures and `python3 tests/rename.test.py` for branding, storage copying, and precedence checks. Both run in CI. Fixtures under `tests/fixtures/legacy/` intentionally preserve the old TRACEFORM name and format byte-for-byte. Fresh results use `STENCILBOX_TEST_OUTPUT`; historical pre-rename test reports are not rewritten.
