# export-wiki
A website that allows users to give github wiki url, and provides different download format options


TODOs:

- [ ] pdf export not adding images
  - [x] add warning on frontend when pdf is selected
- [x] return JSON error from backend if file doesnt work
- [ ] better frontend styles
- [x] Add a max length constraint to wiki_url in ExportRequest (pydantic allows constr(max_length=...))
- [x] refactor get_and_generate_wiki_document, split it up
- [ ] Repo.clone_from could hang or attempt to clone very large repos. add a timeout and max repo size check
- [x] make slowapi per-IP quota
- [x] don't return errors directly, don't leak that info
- [x] dont show Error: ${JSON.stringify(data)} directly on frontend
- [x] better (but general) errors on frontend - e.g. bad url, too many requests, as alert?

- [ ] update backend CORS for deployment
- [ ] dockerize backend
- [ ] deploy 
  - [ ] backend AWS app runner
  - [ ] frontend github pages
- [ ] set up github CI/CD
- [ ] add a modal pop up, if someone has used site a couple times asking for support