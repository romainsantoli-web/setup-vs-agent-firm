# Technical, Performance, Account/Support and UX Complaints in Negative Reviews of Top Mobile Games (2024-2026, Android focus)

> AI-generated research notes - human validation required before use.
> Research date: 2026-10-22. Method: ~20 web searches/fetches. Several primary pages (unstar.app, appfollow.io, notebookcheck.net, mwm.ai) failed DNS resolution from the research environment, so some findings rely on search-engine snippets of those pages rather than full-text reads; this is flagged where relevant. Most evidence is anecdotal (complaint sites, forums, press); a rigorous 2025-2026 quantitative study of mobile-game complaint categories was NOT found.

## Q1. Most frequent technical complaints (crashes, post-update bugs, lag, battery/heat, storage, loading, always-online, outages, low/mid-end Android, fragmentation)

### Takeaway
Industry practitioners group technical complaints into a "bug churn" bucket (crashes, login failures, lag, battery drain, device-specific issues), distinct from "design churn" (economy, matchmaking, ads). Concrete 2024-2026 cases cluster around launch/update crashes (Pokémon TCG Pocket, Pokémon GO 2026), heat/frame drops in high-end 3D gacha titles (Wuthering Waves, Genshin Impact), storage bloat (Genshin ~8-17 GB mobile), and connection/"unreliable network" errors (EA FC Mobile). No reliable 2025-2026 percentage breakdown by category was found.

### Cited Findings
- AppFollow (2026 vendor guide) proposes a tagging scheme where "bug churn" = crashes, login failures, lag, battery drain, device-specific issues; "design churn" = rewards, economy, LiveOps repetition, matchmaking, difficulty spikes; "forced ads" sits under design churn, owned by monetization — [AppFollow, Mobile Game Retention 2026](https://appfollow.io/blog/mobile-game-retention); see also [AppFollow, Bad mobile game update? Protect ratings after release](https://appfollow.io/blog/mobile-game-update-release-issues-reviews-ratings) (full text not retrievable; snippet only).
- Unstar.app published a 2026 industry analysis of 1-3 star reviews from the top 50 mobile games on App Store and Google Play ("what mobile gamers hate most"); search snippet indicates no formal methodology/taxonomy disclosed. Full text could not be fetched (DNS failure) — [Unstar.app blog](https://unstar.app/blog/gaming-app-reviews-what-mobile-gamers-hate-most-2026).
- Older but foundational (pre-2024, flag as old): Khalid et al. manually tagged 1-2 star reviews of 20 iOS apps into 12 complaint types; app crashes, feature requests and functional errors were the most frequent; ethical issues, privacy and hidden costs had the most negative effect on ratings — summarized in [Lin et al., EMSE 2018, "An Empirical Study of Game Reviews on the Steam Platform"](https://sailresearch.github.io/sail-website/data/pdfs/EMSE2018_AnEmpiricalStudyOfGameReviewsOnTheSteamPlatform.pdf).
- Older (flag): McIlroy et al. analyzed ~7,000 Google Play/App Store reviews; ~30% raised more than one technical issue — cited in [Lin et al., EMSE 2018](https://sailresearch.github.io/sail-website/data/pdfs/EMSE2018_AnEmpiricalStudyOfGameReviewsOnTheSteamPlatform.pdf). Hu et al. coded 9,902 low-rated reviews of 19 cross-platform apps; 87.5% had identical complaint tags across Android and iOS — [Hu et al., EMSE 2018](https://sailresearch.github.io/sail-website/data/pdfs/EMSE2018_StudyingTheConsistencyOfStarRatingsAndTheComplaintsIn1&2StarUserReviewsForTopFreeCrossPlatformAndroidAndIOSApps.pdf).
- Steam (not mobile, 2025 student project): analysis of >100,000 Steam reviews across 10 issue categories found most issue types have negligible impact on success metrics, with "Bugs" and "Polish" the notable exceptions — [Liu, Stanford CS191 Spring 2025](https://cs191.stanford.edu/projects/Spring2025/Willam___Liu_.pdf).
- Pokémon TCG Pocket (launch Oct-Nov 2024): "dozens of reports of players unable to jump into the game due to major crashing issues", majority on iPhone but some Android — [TheGamer](https://www.thegamer.com/pokemon-tcg-pocket-is-already-riddled-with-crashing-issues/); [OpenCritic](https://opencritic.com/news/8375/pokemon-tcg-pocket-players-are-struggling-to-play-due-to-crashes). Workaround circulated: change in-game region — [Game8](https://game8.co/games/Pokemon-TCG-Pocket/archives/482819). Emulator crashes after BlueStacks 5 update — [BlueStacks support](https://support.bluestacks.com/hc/en-us/articles/35391217412749-Solution-for-Pok%C3%A9mon-TCG-Pocket-crashing-after-BlueStacks-5-update).
- Pokémon GO v0.421.0 (released 23 July 2026, first update under "Scopely Explore" branding after Scopely acquired Niantic's games business): reported freezing and login failures, release notes said only "Minor bug fixes and performance improvements"; hotfix v0.421.1 around 29 July 2026. Single, unverified source (full page not fetchable) — [mwm.ai](https://mwm.ai/articles/pok-mon-go-v0-421-0-sparks-backlash-with-game-breaking-bugs-under-new-scopely-publisher-july-2026).
- Pokémon GO battery history (old, 2016-2017): version 0.45.0 reportedly drained battery ~30% faster than 0.43.0, attributed to anti-scanner security measures — [Pokémon GO Hub](https://pokemongohub.net/post/news/pokemon-go-drains-a-lot-more-battery-since-the-last-update/). French-language example (2023, old): a Pokémon GO update removed map details and reinstalling didn't fix it for most players — [Dexerto FR, "la dernière MAJ ruine le jeu"](https://www.dexerto.fr/pokemon/derniere-maj-ruine-jeu-pokemon-go-1512560/).
- Wuthering Waves launch (May 2024): Kuro Games acknowledged login issues, performance problems and overheating complaints and promised hotfixes — [Yahoo/Kotaku syndication "Hot New Genshin Impact Clone Suffers Major Launch Day Woes"](https://malaysia.news.yahoo.com/hot-genshin-impact-clone-suffers-201000145.html).
- Wuthering Waves v3.4: mobile players reported frequent stutters and frame drops; phones "running hot after only a few minutes of play", with chipset throttling — [Notebookcheck](https://www.notebookcheck.net/Wuthering-Waves-version-3-4-places-heavy-strain-on-mobile-players.1319209.0.html) (publication date not confirmed; snippet only).
- Single-user anecdote: iQOO 12 (flagship Snapdragon 8 Gen 3) heats up within ~15 minutes playing Wuthering Waves or Genshin Impact at medium settings — [iQOO community](https://community.iqoo.com/in/thread/66322).
- Wuthering Waves low storage can cause force-closes/crashes on Android — [Destructoid](https://www.destructoid.com/how-to-fix-wuthering-waves-crashing-on-android/).
- Storage bloat: Genshin Impact on Android is ~8 GB and grows with updates — [AndroidAyuda](https://en.androidayuda.com/games/general/How-much-space-does-Genshin-Impact-take-up-on-Android-and-other-platforms%3F/); another guide recommends ~17 GB free for mobile (figures conflict; likely version/install-stage differences) — [KeenGamer](https://www.keengamer.com/articles/features/troubleshooting/4-ways-to-fix-the-genshin-impact-insufficient-storage-space-error-on-pc-and-android-devices). "Insufficient storage" install error (-9907) reported — [TheGeekPage](https://thegeekpage.com/genshin-impact-insufficient-storage-space-problem-on-android/).
- EA FC Mobile: player unable to access "FC Mobile 2025" for ~1 week with an "unreliable network" error even via VPN; community manager suggested trying another network (anecdote) — [EA Forums FC Mobile bug reports](https://forums.ea.com/discussions/fc-mobile-bug-reports-en/unreliable-network-account-error-problem-cannot-access-the-game/12095354).
- Brawl Stars: incident tracker lists post-update bugs (character transparency) and inability to play due to connection problems (dates unclear) — [TotalBug](https://www.totalbug.com/?p=2276).
- Kimola auto-generated report on Google Play Games reviews: "functionality praised, performance criticized" (vendor auto-report, low rigor) — [Kimola](https://kimola.com/reports/unlock-insights-google-play-games-user-feedback-analysis-google-play-tr-145041); Monopoly GO report titled "A Fun and Addictive Game with Some Bugs" — [Kimola](https://kimola.com/reports/monopoly-go-fun-addictive-game-bugs-145546).

### Inferences
- The highest-risk technical moments are launch and major updates (TCG Pocket launch, Pokémon GO July 2026 patch, Wuthering Waves launch): staged rollouts, crash-free-session gates and honest patch notes (vs. "minor bug fixes") would directly address the most visible review spikes.
- Heat/throttling complaints appear even on flagship Android chips for open-world 3D gacha games, implying mid/low-end Android users fare worse; a new game should ship scalable graphics presets, frame caps (30/45 fps), and a "battery saver" mode by default.
- Storage bloat (8-17+ GB with additional in-game downloads) is a recurring friction; modular/on-demand asset packs and visible cache-clearing tools are a design lever.
- Vague release notes amplify anger; transparency is a low-cost mitigation.

### Gaps
- No reliable 2025-2026 quantitative share (%) of crashes vs. lag vs. battery vs. storage in 1-2 star mobile game reviews was found (Unstar.app and AppFollow pages unreachable; academic taxonomies are 2015-2018 and not game-specific).
- No systematic data found on Android fragmentation (specific chipsets/brands, e.g., Mali GPUs, Tecno/Infinix) in game reviews, beyond one Şikayetvar complaint about Brawl Stars on a "Techno" device (see Q4).
- Downdetector outage counts for 2025-2026 mobile games not retrieved.
- Mandatory always-online/no offline mode complaints: no specific 2025-2026 source located.

## Q2. Account issues (lost progress, unexplained bans, hacked accounts, no cloud save, failed/undelivered purchases, refunds)

### Takeaway
The dominant account failure pattern in 2025 complaints is "hacked then banned": accounts are compromised, the intruder cheats or misbehaves, and the legitimate owner receives a permanent ban with no workable appeal (Free Fire, Roblox). Roblox complaints add item/currency loss with rollback refusal.

### Cited Findings
- Free Fire: October 2025 complaints describe accounts taken over by hackers then permanently banned for the intruder's activity; players say Garena support confirmed the ban with no appeal path — [Şikayetvar: "My Free Fire Account Was Hacked and Unfairly Banned"](https://www.sikayetvar.com/en/garena-free-fire-us/my-free-fire-account-was-hacked-and-unfairly-banned-need-recovery-help); [Şikayetvar: "Account Hacked and Banned Despite No Cheats"](https://www.sikayetvar.com/en/garena-free-fire-us/free-fire-account-hacked-and-banned-despite-no-cheats-appeal-for-review).
- Free Fire scale of enforcement: 1,087,223 accounts banned globally in one reporting period, 48,390 punished for intentionally playing with hackers; ~48% of bans came from player reports (undated, likely 2020-2021 — flag as old) — [AFK Gaming](https://afkgaming.com/articles/mobileesports/News/5942-free-fire-banned-over-1-million-accounts-for-hacking).
- Garena appeal process exists (state reason + screenshot), reversal "not guaranteed"; guides warn about phishing "unban" forms — [Sportskeeda](https://sportskeeda.com/free-fire/free-fire-id-unban-steps-appeal); [Sportskeeda: why unban tricks don't work](https://www.sportskeeda.com/free-fire/why-unban-tricks-free-fire-work-accounts-banned-hacking).
- Roblox: user claims account compromise with "54 million RAP gone", attackers uploaded illegal material, rollback denied — [Roblox DevForum thread title](https://devforum.roblox.com/t/roblox-account-compromised-support-is-useless-54-million-rap-gone-compromisers-uploaded-illegal-material-involving-minors-rollback-denied/4674997).
- Roblox: attacker enabled 2FA locking out the owner; owner submitted login history, IPs and video and got "insufficient information" without specifics — [ComplaintsBoard](https://www.complaintsboard.com/roblox-corporation-roblox-c1992881).
- Roblox: community list compiling terminated/compromised accounts to deliver at RDC (developer conference) — [Roblox DevForum](https://devforum.roblox.com/t/httpsdiscordggprtjakdw9e-terminated-or-compromised-accounts-compiling-a-list-to-deliver-at-rdc/2536107).
- Whiteout Survival: phishing risk via "cheat" links in videos flagged as unsafe — [Şikayetvar](https://www.sikayetvar.com/en/whiteout-survival-us/i-found-unsafe-cheat-links-in-a-whiteout-survival-video-that-risk-personal-data).

### Inferences
- Design implications: mandatory/strongly encouraged account binding + 2FA, login-anomaly detection, a human-reviewed "compromised account" recovery path distinct from cheat bans, and automatic rollback of actions taken after a detected takeover.
- Bans should state the reason and evidence category; "no explanation + no appeal" is the core grievance.

### Gaps
- No 2025-2026 sourced examples found for: failed/undelivered IAP purchases, refund disputes, guest-account progress loss/no cloud save in specific top games (Monopoly GO, Royal Match, Candy Crush). These are commonly reported anecdotally but no citable source was retrieved in this session.
- PUBG Mobile and Call of Duty Mobile ban/appeal complaints: searched, nothing specific returned.

## Q3. Customer support (bot-only support, no reply, unhelpful responses)

### Takeaway
Roblox is the clearest 2025 case of "AI/bot support loop" complaints: automated rejections, identical scripted replies, and even staff saying they have no control over the AI Support Assistant. Garena (Free Fire) and Century Games (Whiteout Survival) attract "support did nothing" complaints.

### Cited Findings
- Roblox Trustpilot reviewer: "Automated bot support that protects scammers, not players"; another says the case never reached a human supervisor — [Trustpilot NZ, Roblox reviews p.2](https://nz.trustpilot.com/review/www.roblox.com?page=2).
- Roblox: user "stuck in an automated loop for over a month", every ticket receiving an automated rejection without manual evaluation — [Roblox DevForum "Account hacked and roblox support bot does not work"](https://devforum.roblox.com/t/account-hacked-and-roblox-support-bot-does-not-work/3862083).
- Roblox 2025 thread: identical messages that "completely disregard anything I've written in my previous emails"; a reply says real agents handle cases but it can take multiple follow-ups — [Roblox DevForum "Is roblox support run by bots?"](https://devforum.roblox.com/t/is-roblox-support-run-by-bots/3674815).
- Roblox staff reportedly stated they have no control over Roblox's AI Support Assistant — [Roblox DevForum "Customer support does not work"](https://devforum.roblox.com/t/customer-support-does-not-work/4682851).
- Whiteout Survival reviewer: harassment issue unresolved, "Century Games has done nothing" despite proof and repeated outreach; "the ads are a trap" — [JustUseApp Whiteout Survival reviews](https://justuseapp.com/en/app/6443575749/whiteout-survival/reviews).
- EA FC Mobile: community manager response to a week-long lockout was generic network troubleshooting — [EA Forums](https://forums.ea.com/discussions/fc-mobile-bug-reports-en/unreliable-network-account-error-problem-cannot-access-the-game/12095354).

### Inferences
- An AI first-line support agent is acceptable only with a guaranteed, time-bound human escalation for account compromise, bans and payment issues; otherwise it becomes a review-generating liability.
- Support responses should reference the player's submitted evidence (no copy-paste replies) and specify what is missing.

### Gaps
- No quantitative data (response times, % unresolved) for any major mobile publisher's support in 2025-2026.

## Q4. Multiplayer issues (cheaters, bots disguised as players/fake PvP, rigged matchmaking/EOMM, toxicity)

### Takeaway
"Unfair matchmaking" and suspected bots are the most persistent multiplayer complaints for Supercell titles (Brawl Stars, Clash Royale), usually coupled with pay-to-win accusations; cheaters/hackers dominate Free Fire complaints. Supercell has not officially confirmed or denied bots in Clash Royale. Legal risk exists for implying human opponents when bots are used (Skillz v. Papaya).

### Cited Findings
- Brawl Stars: complaint that "70% of my teammates seem like bots"; Nov 2024 post about constantly being matched against Master League players — [Şikayetvar](https://www.sikayetvar.com/en/brawl-stars-us/brawl-stars-matchmaking-pairs-me-with-unfair-opponents-fix-the-system-now).
- Brawl Stars Friendly Battles: "matched against bots that are far too strong... completely throws off the game's balance" — [Şikayetvar](https://www.sikayetvar.com/en/brawl-stars-us/brawl-stars-friendly-battles-plagued-by-overpowered-bots).
- Brawl Stars Feb 2025: hackers and AFK players; players "can't even report them unless we're in ranked matches" — [Şikayetvar](https://www.sikayetvar.com/en/brawl-stars-us/brawl-stars-matchmaking-is-unfair-too-many-hackers-and-afk-players-ruining-the-game).
- Brawl Stars: "Unfair matchmaking on Techno device for 5 years with no solution" (device-specific complaint, possibly Tecno-brand Android) — [Şikayetvar](https://www.sikayetvar.com/en/supercell-us/brawl-stars-unfair-matchmaking-on-techno-device-for-5-years-with-no-solution).
- Brawl Stars community claim (Reddit, via Sportskeeda): players below ~400 trophies "mostly encounter bots" — fan assertion, not Supercell statement — [Sportskeeda](https://www.sportskeeda.com/esports/what-point-feature-brawl-stars-community-discusses-necessity-replays-game?key=skmainfb).
- Clash Royale: Supercell "has not publicly commented" on bots, though the game "likely does have bots" — [Esports.net](https://www.esports.net/news/mobile-games/does-clash-royale-have-bots/).
- Clash Royale Google Play reviews: frustration over matchmaking algorithm and perceived pay-to-win — [Kimola report](https://kimola.com/reports/insightful-clash-royale-feedback-analysis-report-google-play-en-us-154487); Aug 2025 complaint: "the system consistently pairs me against stronger, higher-level opponents" — [Şikayetvar](https://www.sikayetvar.com/en/clash-royale-us/i-face-unfair-matchmaking-and-pay-to-win-advantage-in-clash-royale).
- Legal precedent: Skillz v. Papaya Gaming — a NY federal court found "matched with other players within the same skill level" claims may imply human opponents rather than bots (case ongoing at time of coverage, 2024) — [Tushnet blog](https://tushnet.com/2024/07/29/fair-and-skill-based-may-falsely-imply-absence-of-bots-in-online-gaming/); [Kelley Drye Ad Law Access](https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/bots-and-false-advertising).
- Pokémon TCG Pocket (Jan-Feb 2025): trade restrictions justified as anti-bot/multi-account measures were widely criticized as inaccessible and monetization-driven; players threatened to quit; The Pokémon Company later removed Trade Tokens in favor of Shinedust — [VGC](https://videogameschronicle.com/news/pokemon-tcg-pockets-trading-feature-is-changing-after-fan-backlash); [Pocket Tactics](https://www.pockettactics.com/pokemon-tcg-pocket/trade-update).
- Free Fire: 48,390 players punished for intentionally playing with hackers (older data) — [AFK Gaming](https://afkgaming.com/articles/mobileesports/News/5942-free-fire-banned-over-1-million-accounts-for-hacking).
- AppFollow 2026 guide dedicated to managing toxic players in mobile game reviews (existence confirmed; content not retrieved) — [AppFollow](https://appfollow.io/blog/managing-toxic-players-in-mobile-game-reviews).

### Inferences
- Opaque bot use is a trust and legal risk; a new game should disclose bot matches (label "practice/AI opponent") and avoid marketing language implying all-human PvP.
- Report tools must be available in all modes (not only ranked), with visible outcomes ("action taken on a player you reported").
- Anti-bot measures should not punish legit players (TCG Pocket lesson).

### Gaps
- No official Supercell statement on bots found; no 2025-2026 data quantifying EOMM complaints.
- No sourced 2025-2026 data on PUBG Mobile / CoD Mobile cheater prevalence or Marvel Snap / Marvel Rivals specifics.

## Q5. UX issues (popups, notifications, forced tutorials, accessibility, French localization)

### Takeaway
Little citable 2025-2026 evidence surfaced specifically on popups/notifications/tutorials/localization; the most documented UX-adjacent grievance is the gap between ads and actual gameplay (Last War, Whiteout Survival), and forced ads classified under "design churn".

### Cited Findings
- Last War: Q4 2024 campaign leaning into its own "misleading ads" controversy generated 12.5M+ downloads and #1 US downloads — [Wikipedia: Last War: Survival Game](https://en.wikipedia.org/wiki/Last_War:_Survival_Game).
- Whiteout Survival reviewer: "the game is absolutely nothing like the ad" — [Grand-Screen reviews](https://grand-screen.com/games/whiteout-survival/reviews/).
- ACM study of Facebook mobile game ads: problematic ads fall into misleading content, harmful/offensive content, and omission of information — [ACM DL](https://dl.acm.org/doi/10.1145/3821425); YouTube essay analysis coded ad reactions as disinterested, skeptical, annoyed, sad — [ACM DOI 10.1145/3816734](https://doi.org/10.1145/3816734).
- Older (2017/2020, flag): arXiv studies of in-app ad reviews show ad-related complaints (frequency, intrusiveness, content) measurably hurt ratings — [arXiv 2008.12112](https://arxiv.org/pdf/2008.12112); [arXiv 1702.07681](https://arxiv.org/pdf/1702.07681).
- AppFollow scheme puts "forced ads" under design churn owned by monetization — [AppFollow](https://appfollow.io/blog/mobile-game-retention).
- Pokémon TCG Pocket community: "starting to feel more stressful than fun" (Pokémon official forum thread title, pressure from timers/daily loops) — [Pokémon Community Forums](https://community.pokemon.com/en-us/discussion/18089/pokemon-tcg-pocket-is-starting-to-feel-more-stressful-than-fun).

### Inferences
- Honest store creatives that match gameplay avoid a whole class of 1-star "nothing like the ad" reviews.
- Timer/daily-loop stress is perceived as UX pressure, not only monetization.

### Gaps
- No sourced 2025-2026 French-language review quotes on localization quality, popup clutter, notifications or forced tutorials were found; French search returned mainly PC/console items. Direct scraping of Google Play FR reviews would be needed.
- No accessibility-specific complaint data found.

## Q6. Privacy (permissions, data collection, tracking)

### Takeaway
Regulatory and academic attention to mobile-game privacy rose in 2025-2026: the UK ICO launched a review of 10 popular children's mobile games (Dec 2025), and a 2026 arXiv study finds children's games request fewer permissions but embed tracking SDKs similar to general games.

### Cited Findings
- UK ICO (Dec 2025): monitoring programme on 10 mobile games widely used by children, covering default privacy settings, geolocation controls and targeted ads; supporting research: 76% of respondents worried about personal data sharing, 75% about data collection for advertising — [Hunton privacy blog](https://www.hunton.com/privacy-and-cybersecurity-law-blog/uk-ico-launches-review-of-childrens-privacy-in-mobile-gaming); [SCL](https://www.scl.org/ico-to-examine-how-mobile-games-protect-childrens-online/).
- arXiv 2602.10877 "Beyond Permissions" (Feb 2026): children-oriented Android games request fewer permissions but frequently have configuration-level risks and embed third-party tracking SDKs like general-audience games; permission counts understate exposure — [arXiv](https://arxiv.org/pdf/2602.10877).
- Older (2023, flag): ~20,000 Google Play apps; 4.47% of Family apps request location; 81.25% of Family apps use trackers — [ar5iv 2303.09008](https://ar5iv.labs.arxiv.org/html/2303.09008).
- Older (flag): Khalid et al. found privacy and ethical issues have the strongest negative effect on app ratings — via [Lin et al. EMSE 2018](https://sailresearch.github.io/sail-website/data/pdfs/EMSE2018_AnEmpiricalStudyOfGameReviewsOnTheSteamPlatform.pdf).

### Inferences
- Minimal permissions + minimal ad-SDK footprint + no targeted ads for minors is both a differentiator and regulatory hedge (EU/UK).

### Gaps
- No game-specific 2025-2026 review quotes about permissions found; no data on which named top games draw privacy complaints.

## Q7. Which top games are most cited; studies quantifying categories

### Takeaway
In this session's evidence, the most frequently cited titles for technical/account/support/fairness complaints were Brawl Stars and Clash Royale (matchmaking, bots, pay-to-win), Free Fire (hacked-then-banned, cheaters), Roblox (compromised accounts, bot support), Pokémon TCG Pocket (launch crashes, trade backlash), Pokémon GO (update bugs, battery; July 2026 Scopely patch), Wuthering Waves/Genshin Impact (heat, stutter, storage), EA FC Mobile (connection errors), Whiteout Survival/Last War (misleading ads, support). No rigorous 2025-2026 quantitative study of complaint categories for mobile games was located.

### Cited Findings
- See per-game citations above. Vendor sources (AppFollow, Unstar.app, Kimola) offer taxonomies or auto-generated reports but no transparent, citable percentages retrievable here — [AppFollow review management guide 2026](https://appfollow.io/blog/mobile-game-review-management); [Unstar.app](https://unstar.app/blog/gaming-app-reviews-what-mobile-gamers-hate-most-2026).
- Northwestern (Dec 2025): severely negative mobile-game reviewers sometimes keep playing and spend more, a possible signal of loss of self-control — [Northwestern News](https://news.northwestern.edu/stories/2025/12/customer-ratings-could-help-identify-gamers-who-have-lost-control?fj=1).
- Steam-based taxonomies (Lin et al. 2018, 6,224 games) explicitly compare against mobile app taxonomies — [EMSE 2018](https://sailresearch.github.io/sail-website/data/pdfs/EMSE2018_AnEmpiricalStudyOfGameReviewsOnTheSteamPlatform.pdf).

### Inferences
- Complaint sources skew by genre: competitive PvP (Supercell, Garena) -> fairness/cheat/bot; 3D gacha (HoYoverse, Kuro) -> heat/storage/performance; UGC platforms (Roblox) -> account security/support; 4X (Century Games, FirstFun) -> ads/support; licensed IP (Pokémon) -> launch/update stability.

### Gaps
- Candy Crush, Royal Match, Monopoly GO, Subway Surfers, Marvel Snap, Zenless Zone Zero, Call of Duty Mobile, PUBG Mobile: no specific 2025-2026 technical complaint sources retrieved in this session.
- Several key pages unreachable (DNS failures): unstar.app, appfollow.io, notebookcheck.net, mwm.ai — their content is reported from search snippets only and should be verified.
