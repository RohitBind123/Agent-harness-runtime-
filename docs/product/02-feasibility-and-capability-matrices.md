# 2 — Technical Feasibility Report + iOS and macOS Capability Matrices

*Research conducted 2026-09-06. Current shipping OS is iOS 26 / macOS 26 Tahoe; iOS 27 and macOS 27
"Golden Gate" are at developer beta 8 and expected to ship this month.*

## Evidence markings used throughout

| Mark | Meaning |
|---|---|
| **CONFIRMED** | Stated in official Apple documentation or the App Review Guidelines, cited |
| **LIKELY** | Stated by Apple DTS on the developer forums, or follows necessarily from a CONFIRMED fact |
| **ASSUMPTION** | Our inference from how the APIs compose; not directly sourced |
| **UNKNOWN** | Could not be established from available sources; needs a device spike |
| **IMPOSSIBLE / OS BOUNDARY** | The platform or policy forbids it |

Two access limits affected this research and are disclosed rather than papered over:
`arxiv.org`, `apps.apple.com`, `filexai.com`, `makeitsparkle.co`, `9to5mac.com`, `indiestack.com` and
`www.apple.com` were blocked by the network egress proxy. Where a claim rests on a search-result
summary rather than a fetched primary source, it is marked and the source named.

---

## 2.1 iOS capability matrix

| Capability | iOS verdict | Permission | API / mechanism | Reliability | Background | App Store concern | Notes |
|---|---|---|---|---|---|---|---|
| Pick a folder | **CONFIRMED** | User picks | `UIDocumentPickerViewController` with `.folder` content type (iOS 13+) | High | n/a | 2.5.15 *requires* Files-app and iCloud items be offered | Returns a security-scoped URL |
| Persist folder access across launches | **CONFIRMED** | — | `URL.bookmarkData()` **without** `.withSecurityScope` | High | n/a | none | `.withSecurityScope` is **macOS-only**; on iOS the implicit scope is what persists |
| Open the security scope | **CONFIRMED** | — | `startAccessingSecurityScopedResource()` / `stop…`, iOS 8.0+ | High | n/a | none | Apple: *"Failure to relinquish access … causes your app to leak kernel resources. If sufficient kernel resources leak, your app loses its ability to add file-system locations to its sandbox … until relaunched"* |
| Enumerate files in the granted folder | **CONFIRMED** | Folder grant | `FileManager.enumerator(at:)` | High | Foreground only | none | Descending into subfolders of a granted folder works; ascending to a parent does not |
| Read file metadata | **CONFIRMED** | Folder grant | `URLResourceValues` | High | Foreground only | Privacy manifest: `NSPrivacyAccessedAPICategoryFileTimestamp` required for creation/modification dates | Reason code must be declared |
| Read file contents | **CONFIRMED** | Folder grant | `Data(contentsOf:)`, `NSFileCoordinator` for iCloud items | High | Foreground only | none | Coordinate reads on iCloud-backed files or you race the sync daemon |
| Understand PDFs | **CONFIRMED** | Folder grant | PDFKit (iOS 11+) | High for text PDFs; low for scanned | Foreground only | none | Scanned PDFs need OCR |
| OCR images | **CONFIRMED** | Folder grant | Vision `RecognizeTextRequest` (iOS 18+), on-device, `.accurate` / `.fast` | High | Foreground only | none | Multi-language, auto-detect, custom words |
| Inspect Office documents | **ASSUMPTION** | Folder grant | No first-party API. OOXML is a ZIP; parse yourself or bundle a library | Medium | Foreground only | none | `.doc`/`.xls` legacy formats are materially harder |
| Create folders | **CONFIRMED** | Folder grant (read-write) | `FileManager.createDirectory` | High | Foreground only | none | |
| Rename / move | **CONFIRMED** | Folder grant | `FileManager.moveItem` inside the granted scope | High | Foreground only | none | Cross-scope moves need both scopes open |
| Copy | **CONFIRMED** | Folder grant | `FileManager.copyItem` | High | Foreground only | none | |
| Delete | **CONFIRMED** *(capability)* | Folder grant | `FileManager.removeItem` / `trashItem` | High | Foreground only | none | **There is no user-visible Trash for arbitrary Files-app locations.** `trashItem` availability outside the app container is **UNKNOWN**; treat delete as unrecoverable |
| Duplicate detection | **CONFIRMED** | Folder grant | Our own content hashing | High | Foreground only | none | Deterministic; no model needed |
| Semantic classification (on-device) | **CONFIRMED, with a hard limit** | — | Foundation Models `SystemLanguageModel`, iOS 26+ | Medium | Foreground only | none | **4,096-token context window per session** (Apple's own "Managing the context window"). Apple-Intelligence-capable devices only |
| Semantic classification (cloud) | **CONFIRMED** | Network | Any model provider over HTTPS | High | Foreground only | 5.1.2(i): must *"clearly disclose where personal data will be shared with third parties, including with third-party AI, and obtain explicit permission"* | The disclosure requirement is explicit and recent |
| Semantic search | **CONFIRMED** | — | Our own index (SQLite FTS + embeddings) | High | Foreground only | none | |
| Watch a folder for changes | **IMPOSSIBLE (practically)** | — | `DispatchSource` vnode / `NSMetadataQuery` / `NSFilePresenter` | **Low** | **No** | none | vnode sources are **not recursive**, need one file descriptor per directory against a 256-fd limit, tell you *that* something changed but not *what*, and **do not resume the app in background**. `NSMetadataQuery` does not work on open-in-place Files directories. **The agent must scan on open** |
| Execute commands / shell / git | **IMPOSSIBLE — policy and OS** | — | — | — | — | **2.5.2** | *"may not download, install, or execute code which introduces or changes features or functionality of the app"* |
| Long-running job, user-initiated | **CONFIRMED** | — | `BGContinuedProcessingTaskRequest`, iOS 26+ | Medium | Yes, with user-visible UI | 2.5.4 | Must be submitted from the foreground *"as a result of a person's action, such as tapping a button"*; shows `title`/`subtitle` to the user |
| Opportunistic background work | **CONFIRMED, unreliable** | — | `BGProcessingTaskRequest`, iOS 13+ | **Low** — system decides | Yes | 2.5.4 | `requiresExternalPower`, `requiresNetworkConnectivity`. No scheduling guarantee |
| Recover after app termination | **CONFIRMED** *(our own work)* | — | Durable state in our container + checkpointing | High | n/a | none | The OS gives no drain signal; every write must assume it is the last |
| Durable state | **CONFIRMED** | — | SQLite in the app container | High | n/a | none | |
| Sync state across devices | **CONFIRMED** | iCloud account | CloudKit | High | System-managed | none | Sync the **agent's** state, not the user's files |
| See other apps' files | **IMPOSSIBLE — OS BOUNDARY** | — | — | — | — | — | Sandbox |
| Provide files *to* other apps | **CONFIRMED, narrow** | — | File Provider extension | High | System-managed | 2.5.1 | Apple: an extension provides access **only to files your own app manages**. Not a route to reading anyone else's |

### The three iOS findings that change the product

**1. There is no background agent on iOS.** The combination of "no recursive watch", "vnode sources do
not resume the app in background", and "`BGContinuedProcessingTask` must originate in a user tap"
means the honest model is: **the user opens the app, the agent scans, proposes, acts, verifies, and
stops.** Any PRD sentence implying an agent that quietly keeps your phone tidy is false.

**2. The on-device model is a 4,096-token component, not a reasoner.** Apple's own guidance is to
split large tasks across sessions, keep to 3–5 tools per request, and handle
`LanguageModelError.contextSizeExceeded` by starting a new session. This is not a limitation to work
around; it *forces* the correct architecture — the model classifies bounded extracted text into a
typed schema, and deterministic code does the planning, the path arithmetic and the mutation. That is
the same discipline the specification states as design rule 14.

**3. Delete has no undo.** On macOS you can move to Trash. In an arbitrary Files-app location on iOS
there is no equivalent guarantee. **The MVP must not delete.** Quarantine inside the granted scope,
and make deletion a separate, explicitly gated, later operation.

### iOS items that remain UNKNOWN and need a device spike

| # | Question | Why it matters | Spike |
|---|---|---|---|
| S1 | Can one folder-pick grant cover the *root* of "On My iPhone" or iCloud Drive, or only a subfolder? | Determines whether onboarding is one tap or twenty | ~30 min in Xcode on a real device |
| S2 | Are third-party File Provider folders selectable in `.folder` picker mode today? | Determines whether Dropbox/Drive users are reachable | ~30 min, same spike |
| S3 | Does `trashItem` work on a security-scoped URL outside the container? | Decides whether "delete" can ever be offered | ~15 min |
| S4 | Does a resolved bookmark survive an iCloud file being evicted and re-downloaded? | Decides whether the world model can key on bookmarks | ~1 hour |

---

## 2.2 macOS capability matrix

| Capability | macOS verdict | Permission | API / mechanism | Reliability | Background | Distribution concern | Notes |
|---|---|---|---|---|---|---|---|
| Pick a folder | **CONFIRMED** | User picks | `NSOpenPanel` with `canChooseDirectories` | High | n/a | none | |
| Persist folder access | **CONFIRMED** | — | Security-scoped bookmark with `.withSecurityScope` | High | n/a | Requires `com.apple.security.files.user-selected.read-write` (macOS 10.7+) | |
| Enumerate / read / metadata | **CONFIRMED** | Folder grant, or FDA | `FileManager` | High | Yes | none | |
| OCR / PDF | **CONFIRMED** | Folder grant | Vision `RecognizeTextRequest` (macOS 15+), PDFKit | High | Yes | none | |
| Create / rename / move / copy | **CONFIRMED** | Folder grant | `FileManager` | High | Yes | none | |
| Delete **with undo** | **CONFIRMED** | Folder grant | `FileManager.trashItem` | High | Yes | none | Real Trash. This is a genuine macOS advantage over iOS |
| Watch for changes | **CONFIRMED** | Read permission on the path | `FSEvents` (`FSEventStreamCreate`) | High | Yes | Returns `nil` if you lack read permission — so scope grants gate it | Recursive, coalesced, has a replay cursor via `FSEventStreamEventId` |
| Execute commands / git | **CONFIRMED, with a caveat** | — | `Process` / `posix_spawn` | High | Yes | See below | Apple DTS: *"Things that aren't apps always inherit the sandbox from the parent process."* A sandboxed app **can** spawn `git`; `git` then runs **inside the app's sandbox** |
| Give a child process file access | **LIKELY** | — | Pass an **implicit** security-scoped bookmark to the child | Medium | Yes | none | Apple DTS forum guidance, not a documentation page. Needs a spike |
| `com.apple.security.inherit` | **CONFIRMED** | — | Entitlement on a bundled helper | High | — | Apple DTS: *"exists primarily to act as a marker for App Review"*; inheritance happens by default | |
| Launch another *app* | **CONFIRMED** | — | `NSWorkspace` / `open` | High | Yes | The launched app gets **its own** sandbox, not yours | Not a child process you control |
| Full Disk Access | **CONFIRMED as user-granted only** | User, in System Settings | TCC `kTCCServiceSystemPolicyAllFiles` | High once granted | Yes | **Cannot be requested programmatically.** TCC.db is SIP-protected | Practical only for Developer ID distribution |
| Background execution | **CONFIRMED** | — | A real long-running process, `LaunchAgent`, or `NSBackgroundActivityScheduler` | High | **Yes — genuinely** | `LaunchAgent` outside MAS | This is the single biggest asymmetry with iOS |
| Durable state | **CONFIRMED** | — | SQLite | High | Yes | none | |
| Sync state across devices | **CONFIRMED** | iCloud account | CloudKit | High | Yes | none | |
| Distribution: Mac App Store | **CONFIRMED** | — | — | — | — | **Sandbox mandatory** | Unified billing with iOS; capability ceiling is lower |
| Distribution: Developer ID | **CONFIRMED** | — | — | — | — | Notarization + hardened runtime required; **sandbox optional** | Higher capability ceiling; you own trust and updates |

### The macOS finding that forces a product decision

**Mac App Store and Developer ID are not two channels for the same app; they are two different
products.** Under the sandbox, the agent can still do all of the file work — enumerate, read, OCR,
move, rename, trash, watch — inside user-granted scopes, and it can even run `git`, confined. What it
loses is anything needing Full Disk Access, anything needing the user's real `~/.gitconfig` and SSH
keys, and any credible "works on my whole machine" story.

Recommendation, argued in report 4: **ship sandboxed and Mac App Store first.** The capability the
sandbox costs you is precisely the capability whose blast radius you cannot yet contain, and the MVP
should not want it.

---

## 2.3 Cross-platform: what "one agent, two environments" actually means

Honest comparison of the *same* agent capability on each platform:

| Runtime property the architecture assumes | macOS | iOS |
|---|---|---|
| A process that keeps running | Yes | **No** |
| Observe the environment without being asked | Yes (FSEvents) | **No** |
| Resume work after a crash without the user | Yes | **No** — needs the user to reopen |
| Execute arbitrary capabilities | Yes (sandbox-confined) | **No** (2.5.2) |
| Reversible delete | Yes (Trash) | **No** |
| Local reasoning | Yes, and cloud too | 4,096 tokens on-device, or cloud |
| Durable state, memory, taxonomy | Yes | Yes |
| Verification of outcomes | Yes | Yes |

Five of eight rows differ. That is the fact the product strategy has to be built on, not around: the
Brain and its durable state are genuinely shared; the *runtime* is not the same runtime. Report 4
takes the position that saying so plainly is a better product than pretending otherwise.

---

## 2.4 App Store policy constraints, quoted

| Guideline | Text | Effect on this product |
|---|---|---|
| **2.5.2** | *"Apps should be self-contained in their bundles, and may not read or write data outside the designated container area, nor may they download, install, or execute code which introduces or changes features or functionality of the app, including other apps."* | **No agent-authored code execution on iOS.** The document-picker grant is the sanctioned exception to the container rule; nothing about generated code is |
| **2.5.4** | *"Multitasking apps may only use background services for their intended purposes: VoIP, audio playback, location, task completion, local notifications, etc."* | Background work must be genuine task completion, declared as such |
| **2.5.15** | *"Apps that enable users to view and select files should include items from the Files app and the user's iCloud documents."* | A **requirement to include**, satisfied by using `UIDocumentPickerViewController`. Note: an earlier working assumption that "apps primarily acting as iCloud file managers need additional functionality" **is not in the current guidelines** — that claim is now retracted |
| **4.2** | *"If your app is not particularly useful, unique, or 'app-like,' it doesn't belong on the App Store."* | A thin classifier wrapper is at risk; a staged/reviewable/undoable mutation engine is not |
| **5.1.2(i)** | *"You must clearly disclose where personal data will be shared with third parties, **including with third-party AI**, and obtain explicit permission before doing so."* | If document text leaves the device, this is an explicit, per-user consent obligation |
| **5.1.2(ii)** | *"Data collected for one purpose may not be repurposed without further consent."* | Document content used for classification may not be reused for model training without separate consent |

---

## 2.5 Feasibility verdict

**Can the product be built? Yes on macOS. Partly on iOS, and not in the form the vision describes.**

| Vision claim | Verdict |
|---|---|
| "observes a real environment" | macOS **yes** (FSEvents). iOS **no** — scan-on-open only |
| "maintains a grounded world model" | **Yes**, both — beliefs keyed by path + content hash, invalidated by observed effects |
| "durable memory" | **Yes**, both |
| "pursues user goals, plans, executes through controlled capabilities" | **Yes**, both, within granted scopes |
| "verifies real-world outcomes" | **Yes**, both — and deterministically, which is the strongest part of the story |
| "recovers from failures" | macOS **yes**. iOS **yes, but only when the user returns** |
| "records trajectories, evaluates, evolves" | **Yes** technically; the evolution loop is far beyond MVP |
| "terminal / processes / git on Mac" | **Yes** if you accept sandbox confinement, or ship Developer ID |
| "same agent on iPhone and Mac" | **Half true.** Same Brain, same memory, same taxonomy. Materially different runtime |
