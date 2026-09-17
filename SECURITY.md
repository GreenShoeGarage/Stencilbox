# Security and privacy

STENCILBOX processes project files locally. It has no account system, application backend, runtime telemetry, or application network requests. A static host can still record ordinary page requests. JSON project files include settings and optional notes; review them before sharing.

## Reporting a problem

Do not place credentials, private project data, or working security exploits in a public issue. Use GitHub private vulnerability reporting when the repository maintainer has enabled it. Otherwise contact the maintainer through a channel they have actually published; this template does not invent a security address or promise response times.

Repository owners should configure their preferred private reporting channel before inviting confidential reports. Regular UI and geometry bugs belong in the bug-report template, with sanitized reproductions.

## Boundaries

Browser storage is not encrypted backup. Keep JSON copies somewhere appropriate for your data. Import validation and geometry checks reduce mistakes but are not a security audit, manufacturing certification, or physical strength guarantee. Developer dependencies and GitHub Actions run only during development/CI; review dependency updates before merging.
