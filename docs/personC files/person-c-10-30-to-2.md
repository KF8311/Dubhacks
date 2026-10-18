# Person C — 10:30 PM–2:00 AM checklist

Done when the purge, skeletons, empty state, and error banner are on screen, an unknown receipt link says it was not found, and the page does not scroll sideways at 1024px or 1280px.

This block does not record the backup video or freeze the features. That starts at 2:00 AM.

## Already built in earlier blocks

- [x] `PurgeOverlay` covers the screen, then removes danger cards. Reduced motion finishes immediately.
- [x] A check that has not arrived yet renders a skeleton row, not a blank gap.
- [x] `no_trusted_option` shows `EmptyState` with the reason and Start over. It is not an error banner.
- [x] A session error shows `ErrorBanner` and Dismiss clears it.
- [x] `/r/:shareId` renders the receipt. An unknown id shows “Receipt not found.”

## This block

- [x] Finding products shows an alert and stays on the question screen when the API cannot be reached.
- [x] At 1024px the document does not scroll horizontally. Two columns, overflow 0.
- [x] At 1280px the document does not scroll horizontally. Three columns, overflow 0.
