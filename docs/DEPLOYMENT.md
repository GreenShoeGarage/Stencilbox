# Run, publish, and host STENCILBOX

## Run without installation

Open the repository's `index.html`. That one file contains the working app, renderer, triangulator, CSS, and vendor attribution. No Node.js, Python, package manager, server, or network access is required to use it.

For a local HTTP origin during development, run this in the repository folder and open the printed localhost address:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Browser policy controls local storage and downloads. Export JSON for durable backups. The downloaded HTML works offline; a hosted tab is not promised indefinite offline caching, and there is no service worker.

## Put the repository on GitHub

Unzip the repository archive. The top-level `stencilbox/` is the repository folder; **its contents** belong at the repository root, so `index.html`, `README.md`, and `.github/` are siblings. Keep hidden dotfiles, including `.github/`.

Create an empty GitHub repository named `stencilbox`, without another README or license. Then run the following inside the extracted folder, using the remote URL shown by your new repository:

```sh
git init -b main
git add .
git commit -m "Initial STENCILBOX v1.0.0 release"
git remote add origin YOUR_REPOSITORY_REMOTE_URL
git push -u origin main
```

Replace `YOUR_REPOSITORY_REMOTE_URL` before running the command. Choose the repository visibility deliberately. This archive contains no `.git` directory, stored credentials, remote binding, or fabricated commit history.

GitHub Desktop is also suitable: initialize the extracted directory as a local repository, commit its contents, and publish it. Do not upload the ZIP itself as a substitute for the source tree.

Suggested repository description: **Local-first geometric stencil studio. Generate, manipulate, and export 3D-printable stencils as STL and editable JSON.**

Suggested topics: `stencil`, `generative-art`, `3d-printing`, `stl`, `offline`, `local-first`, `javascript`.

## GitHub Pages: optional, manual by default

Set the repository's **Settings → Pages → Build and deployment → Source** to **GitHub Actions**. Then choose **Actions → Deploy GitHub Pages → Run workflow**, selecting `main`.

The deployment first runs the reusable CI workflow. Only if every check succeeds does it stage the checked-in app and license notices, upload the Pages artifact, and deploy. The workflow run exposes the resulting site address. Other branches are deliberately skipped. Rename the `main` branch references in `pages.yml` when using another default branch.

Only `_site/` is published: `index.html`, `.nojekyll`, `LICENSE`, `THIRD_PARTY_NOTICES.md`, and `EARCUT-LICENSE.txt`. Source files, example projects, tests, and workflow files are not copied to the Pages site. They remain visible in a public repository.

To enable deployment on each push to `main`, uncomment these two lines below `workflow_dispatch` in `.github/workflows/pages.yml`:

```yaml
  push:
    branches: [main]
```

This is optional. Manual-by-default deployment prevents a first repository push from failing solely because Pages has not been enabled. CI runs on pushes and pull requests regardless. No custom token or secret is required by the provided workflows, although repository or organization policies may require approvals.

Do not add another Pages-generated workflow while also using this one. Choose one publishing mechanism. No custom domain or `CNAME` has been assumed or configured.

## Existing static hosting

For an address such as `mbparks.com/stencilbox/`, upload the root `index.html` as `/stencilbox/index.html` in that site's document root. The file uses no external runtime assets and works in a subfolder. Retain the license notices when distributing a copy.

Do not upload `src/index.template.html` instead: it is a developer template, not the built application. Do not upload the whole repository ZIP to the hosting folder and expect it to run.

## Troubleshooting

**CI reports stale HTML:** run `python3 build.py`, review changes, and commit both edited source and `index.html`.

**Pages is skipped:** select `main` when manually running the deployment, or adjust the workflow's branch conditions for the actual default branch.

**Pages configuration fails:** confirm Source is GitHub Actions, Actions are allowed, and repository/environment permissions permit Pages deployments. Run the deployment again after configuring Pages.

**The app looks old:** confirm the correct `index.html` was replaced, reload without cache, and check the visible version. Browser storage follows the origin, so use exported JSON to migrate projects.

**Storage is unavailable:** the app remains usable but browser autosave may fail. Use Save JSON and keep the resulting file. Moving files, private browsing, or clearing site data can change persistence.

## Official workflow references

Verified for this repository packaging on September 17, 2026:

- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Configuring a Pages publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Reusing workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)

These are documentation links, not application runtime requests. Remote workflow execution and deployment require the repository to be published; they have not been executed on a GitHub account as part of preparing this archive.
