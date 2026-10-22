# Public documentation maintenance

`public-release.json` contains the public version, platform, release status, exact application filenames, requirements and localized navigation. Detailed guides and legal notices retain their own content.

After a reviewed metadata change, run `python tools/check_public_docs.py --write`. Review the generated README summaries, guides and `docs/release-notes.*.md`. The three release-note files provide the same five sections for future releases: changes, compatibility, installation, limitations and checksums. Replace the commit-list link with the reviewed changelog for that release before publication. These files do not update an existing GitHub release or archive.

Run `python tools/check_public_docs.py --online --published` to check local pages, application version declarations, published release assets and localized HTML guide availability. The Public documentation workflow runs on pull requests, pushes and weekly. A green documentation check does not verify application behavior, signing or a clean-machine installation.

Preview links target the exact reviewed release. Source-only projects have no binary download button. Published archives, licenses and repository visibility require their own review.

Temporary technical results belong in Actions artifacts. Do not use user-facing Releases for diagnostic self-tests. Screenshots and attachments must exclude credentials and private user content; label demonstration data honestly.

For the profile catalog, run `python tools/check_public_docs.py --refresh-catalog --write` after project metadata PRs are merged. The weekly check compares catalog entries to each project on its current main branch.


Applications distributed in another project’s installer declare `shared_distribution` with `repo`, distribution `version`, `tag`, `release_url` and `application_versions`. The application keeps its own `version` and uses `tag: null` when it has no separate GitHub release. The validator checks asset URLs, status and files against the declared distribution repository; it does not treat the bundle version as the application version. The catalog must copy this declaration from the application metadata.

## Visual review before publication

- Artwork with its own rounded border must not receive a second, incompatible CSS `border-radius` or `overflow: hidden` mask. Keep the PeakMP3 banner image unclipped: its SVG already defines the complete rounded outline. If a mask is necessary, derive its radius from the artwork's scaled geometry.
- Inspect all four corners and the entire outline in the rendered page at actual desktop and phone sizes. An undamaged SVG or a correct GitHub README preview does not prove that the website's CSS preserves the frame.
- Compare website and README versions of shared artwork. Preserve screenshot aspect ratios; avoid cropped interface controls, distorted screens and blurred cutout edges.
- Review RU/DE/EN, available light/dark themes, long labels and enlarged text. Check for horizontal overflow, matching control heights, and visible gaps between text, buttons and divider lines.
- Click the user-facing destinations: guides must open as published HTML pages, not GitHub HTML source views; each project's actions must point to that project.
- Retain before/after browser screenshots for visual changes. Automated documentation checks complement this review; they do not replace it.
