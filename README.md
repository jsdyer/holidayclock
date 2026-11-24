# Holiday Clock

Compare two country or regional holiday calendars, export a calendar, and count working days using explicit assumptions. The app runs at https://coolcode.ca/holidayclock/ without an account or key.

<!-- coolcode:guide -->
Compare any supported countries and first-level regions, with British Columbia and Nova Scotia as the starting pair. Canada can use nominal or observed dates; other calendars retain their own substitute rules. Export a comparison CSV, dated JSON receipt or all-day ICS calendar. The working-day planner uses public holidays, your selected weekend weekdays and extra closure dates, counting each date once. Confirm applicable workplace rules: these community calendars are not statutory or ATIP deadline advice.
<!-- /coolcode:guide -->

## Use it

1. Choose both countries and, where available, a province, territory or state. Canada requires a province, territory or the federal calendar. Other countries permit country-wide rules.
2. Pick a year from 2013 to 2038 and compare. The defaults are BC and Nova Scotia. Presets are shortcuts, not the supported list.
3. Search names or dates, or show dates that occur in only one calendar. Counts refer to distinct dates; the same date can contain different named holidays.
4. Download the full comparison as CSV or JSON, or either calendar as an ICS file. These are downloaded files, not automatically updating calendar subscriptions. Filters do not remove records from exports.
5. In the working-day planner, select either displayed calendar. Set a range, non-working weekdays, endpoint inclusion and optional extra closures. Public holidays are closures; bank, optional, school and observance types are not automatically closures. Every date is classified once, with weekends taking precedence over holidays.

A useful example is September 30, 2026. The BC and federal source calendars include National Day for Truth and Reconciliation. It is not shown as a general NS paid holiday. This does not describe all NS public-sector or individual employer arrangements. Nova Scotia Remembrance Day has separate legislation and is not included in this source’s NS paid-holiday set.

## Sources and date meanings

Canada Holidays is a community-maintained project with links to provincial sources, not an official government API. The public API supports 2013–2038. The local cache contains actual records for 2025–2028 captured on November 23, 2026. Each refresh replaces that four-year rolling window. Source: https://canada-holidays.ca/api

Canadian nominal dates are the named holiday dates. Observed dates select the source's observedDate field. Whether that is a day off for a particular worker depends on employment rules and substitutions. The federal calendar refers to the source's federal flag, not every workplace in Canada.

The 207 country choices include Canada. Other countries and their first-level regions calculate locally using date-holidays 3.39.2. Country-wide rules can omit local holidays. Religious dates, one-off declarations, future legislative changes and historical rules need confirmation. The app displays the library's supplied English labels and public/bank/observance/optional/school categories without upgrading them into legal entitlements. Source: https://github.com/commenthol/date-holidays

The library's calendar data is CC BY-SA 4.0, by commenthol and contributors, with source attributions in web/vendor/DATE-HOLIDAYS-LICENSE.txt. Code is ISC; bundled dependency licences are in web/vendor/BUNDLE-LICENSE.txt. This app does not modify the upstream calendar rules. Exported international calendar records retain source attribution; their data remains subject to CC BY-SA 4.0. Licence: https://creativecommons.org/licenses/by-sa/4.0/

International substitute dates follow the library’s calendar-year output: for example, Washington’s December 31, 2021 observed New Year holiday belongs to the 2021 calendar, even though its named holiday is January 1, 2022. Canadian observed dates preserve their nominal date in each record.

The planner accepts endpoints up to 366 days apart, so including both can count 367 calendar dates. It loads coverage for every year in that range, including cross-year and fiscal-year ranges. It is a generic calendar calculation, not a statutory, court, tax or ATIP deadline calculator. Dates use calendar-day arithmetic at UTC noon to avoid daylight-saving shifts.

## Privacy and requests

No keys or registration. Plans, extra closures and selections remain in tab memory; no localStorage is used. International calendars are calculated from the local bundle. Canadian years already cached need no upstream request. An uncached Canadian year sends only a year parameter to canada-holidays.ca using a request with no credentials or referrer. Network providers still see ordinary connection metadata. Downloads remain under your control. The shared CoolCode counter records aggregate opens and excludes form inputs.

Provider failures preserve the last valid comparison and count. Invalid data cannot enter the Canadian cache. Changing a comparison while a request is pending cannot let a late response overwrite a newer comparison. The source timestamp is displayed separately from the receipt generation time.

## Expand or customize

Edit web/config.json to change defaultA, defaultB, presets, weekendDays or seedYearOffsets. Country and region options come from the library rather than a fixed showcase list. Use codes available through countries and regions in web/model.mjs. Canadian provinces use two-letter codes and FED selects the federal calendar. The date range cannot exceed the Canadian API's 2013–2038 coverage unless its contract and app validation are reviewed together.

Add extra workplace closures directly in the planner. To change permanent calendar rules, update the vendored date-holidays release deliberately and preserve its licences, attributions and bundle reproducibility. Its 1.5 MB bundle is used for a concrete purpose: global, offline holiday calculations without passing user plans to a service. No npm installation is needed to build or run this app.

To refresh Canadian records manually:

```sh
python3 scripts/refresh.py
```

The collector fetches the configured rolling years, validates every response and atomically replaces web/data/canada.json only after all years succeed. GitHub Actions runs this monthly and on manual dispatch when refresh_data is selected. It retains the cache in Git history and builds the captured commit. Ordinary pushes and PRs build offline from the retained cache. A failed refresh prevents deployment and preserves the last successful site. GitHub can suspend public-repository schedules after 60 days without repository activity.

The international rule library is not updated automatically. Review upstream changes and update its version and reviewedAt in config when deliberately replacing the bundle.

## Build and check

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

Node tests cover leap dates, fiscal-year ranges, Canadian jurisdiction differences, observed substitutes, duplicate closures, CSV safety, ICS folding and source failure preservation. Python tests cover the static builder and atomic refresh. CI also runs the browser flow and narrow-screen check in tests/browser_smoke.py at a project subpath.

The app source is in web/, with transformations in model.mjs, Canadian cache handling in service.mjs and DOM code in app.mjs. The Pages build is in scripts/build.py. Keep all app assets relative, do not add a CNAME, and keep tool.json and this practical guide aligned with behaviour.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
