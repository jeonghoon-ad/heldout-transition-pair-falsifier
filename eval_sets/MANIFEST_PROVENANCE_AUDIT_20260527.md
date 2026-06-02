# Manifest Provenance Audit

Generated: 2026-05-27 22:39 KST

Scope: Phase 1/2/3/4 S3 x S3 long-horizon evaluation sets.

Finding: raw per-phase evaluation arrays were not persisted as separate files for Phases 2/3/4. The runner uses the same deterministic `generate_eval_arrays(spec, seed, eval_len, n_test)` call for every phase. Recomputed token+label hashes are identical across phases for each `(seed, eval_len)`, so the audit certifies identity by deterministic regeneration from the recorded runner and config. Future public runs should persist the actual token arrays if independent byte-for-byte replay is required.

| phase | seed | eval_len | eval_set_sha256 |
| --- | ---: | ---: | --- |
| Phase 1 expanded | 20260525 | 524288 | `0576474b28707e6abf5945a3218445bc84b58af495975e6569a43e697d233bf4` |
| Phase 1 expanded | 20260525 | 1048576 | `c80f4f84f8ceaf7191bd64ea72be4c23f7364b44f1601f522b41f2ebc2a0d307` |
| Phase 1 expanded | 20260526 | 524288 | `35f9116c1aa51718bb9662f0af75072486b6032798e01ea8d89c9510cc8a1e34` |
| Phase 1 expanded | 20260526 | 1048576 | `2e80d38470b1385a296dbbab6864b32564a93caec400ce3e4c7fb36de10dbc5e` |
| Phase 1 expanded | 20260527 | 524288 | `7ecf9aae761647ba7d76c8a8a0976151d88ee34607d7f85b2460c11d99c5605a` |
| Phase 1 expanded | 20260527 | 1048576 | `0595b4d03c0e38d7753bfbd911bb61f1373cf2a240836b462b40c6d3c4ea6ea9` |
| Phase 1 expanded | 20260528 | 524288 | `c915af9d03f55e11e127be1990f70674101060330f0b3a3fb251bc133985f331` |
| Phase 1 expanded | 20260528 | 1048576 | `9226357cb0a544a6d3cb07546a7f35c15b0a2e33561e9ceb17a644642edcd22f` |
| Phase 1 expanded | 20260529 | 524288 | `42e7bfa695cc080334cd8d51d4a9920784d90948343e8c73a9db55bd1beec6fa` |
| Phase 1 expanded | 20260529 | 1048576 | `bc68f08df128608da747652472bb1b0b33019f3d759c3a6502f51d65436be411` |
| Phase 2 projected GRU | 20260525 | 524288 | `0576474b28707e6abf5945a3218445bc84b58af495975e6569a43e697d233bf4` |
| Phase 2 projected GRU | 20260525 | 1048576 | `c80f4f84f8ceaf7191bd64ea72be4c23f7364b44f1601f522b41f2ebc2a0d307` |
| Phase 2 projected GRU | 20260526 | 524288 | `35f9116c1aa51718bb9662f0af75072486b6032798e01ea8d89c9510cc8a1e34` |
| Phase 2 projected GRU | 20260526 | 1048576 | `2e80d38470b1385a296dbbab6864b32564a93caec400ce3e4c7fb36de10dbc5e` |
| Phase 2 projected GRU | 20260527 | 524288 | `7ecf9aae761647ba7d76c8a8a0976151d88ee34607d7f85b2460c11d99c5605a` |
| Phase 2 projected GRU | 20260527 | 1048576 | `0595b4d03c0e38d7753bfbd911bb61f1373cf2a240836b462b40c6d3c4ea6ea9` |
| Phase 2 projected GRU | 20260528 | 524288 | `c915af9d03f55e11e127be1990f70674101060330f0b3a3fb251bc133985f331` |
| Phase 2 projected GRU | 20260528 | 1048576 | `9226357cb0a544a6d3cb07546a7f35c15b0a2e33561e9ceb17a644642edcd22f` |
| Phase 2 projected GRU | 20260529 | 524288 | `42e7bfa695cc080334cd8d51d4a9920784d90948343e8c73a9db55bd1beec6fa` |
| Phase 2 projected GRU | 20260529 | 1048576 | `bc68f08df128608da747652472bb1b0b33019f3d759c3a6502f51d65436be411` |
| Phase 3 projected structured SSM | 20260525 | 524288 | `0576474b28707e6abf5945a3218445bc84b58af495975e6569a43e697d233bf4` |
| Phase 3 projected structured SSM | 20260525 | 1048576 | `c80f4f84f8ceaf7191bd64ea72be4c23f7364b44f1601f522b41f2ebc2a0d307` |
| Phase 3 projected structured SSM | 20260526 | 524288 | `35f9116c1aa51718bb9662f0af75072486b6032798e01ea8d89c9510cc8a1e34` |
| Phase 3 projected structured SSM | 20260526 | 1048576 | `2e80d38470b1385a296dbbab6864b32564a93caec400ce3e4c7fb36de10dbc5e` |
| Phase 3 projected structured SSM | 20260527 | 524288 | `7ecf9aae761647ba7d76c8a8a0976151d88ee34607d7f85b2460c11d99c5605a` |
| Phase 3 projected structured SSM | 20260527 | 1048576 | `0595b4d03c0e38d7753bfbd911bb61f1373cf2a240836b462b40c6d3c4ea6ea9` |
| Phase 3 projected structured SSM | 20260528 | 524288 | `c915af9d03f55e11e127be1990f70674101060330f0b3a3fb251bc133985f331` |
| Phase 3 projected structured SSM | 20260528 | 1048576 | `9226357cb0a544a6d3cb07546a7f35c15b0a2e33561e9ceb17a644642edcd22f` |
| Phase 3 projected structured SSM | 20260529 | 524288 | `42e7bfa695cc080334cd8d51d4a9920784d90948343e8c73a9db55bd1beec6fa` |
| Phase 3 projected structured SSM | 20260529 | 1048576 | `bc68f08df128608da747652472bb1b0b33019f3d759c3a6502f51d65436be411` |
| Phase 4 projected bag | 20260525 | 524288 | `0576474b28707e6abf5945a3218445bc84b58af495975e6569a43e697d233bf4` |
| Phase 4 projected bag | 20260525 | 1048576 | `c80f4f84f8ceaf7191bd64ea72be4c23f7364b44f1601f522b41f2ebc2a0d307` |
| Phase 4 projected bag | 20260526 | 524288 | `35f9116c1aa51718bb9662f0af75072486b6032798e01ea8d89c9510cc8a1e34` |
| Phase 4 projected bag | 20260526 | 1048576 | `2e80d38470b1385a296dbbab6864b32564a93caec400ce3e4c7fb36de10dbc5e` |
| Phase 4 projected bag | 20260527 | 524288 | `7ecf9aae761647ba7d76c8a8a0976151d88ee34607d7f85b2460c11d99c5605a` |
| Phase 4 projected bag | 20260527 | 1048576 | `0595b4d03c0e38d7753bfbd911bb61f1373cf2a240836b462b40c6d3c4ea6ea9` |
| Phase 4 projected bag | 20260528 | 524288 | `c915af9d03f55e11e127be1990f70674101060330f0b3a3fb251bc133985f331` |
| Phase 4 projected bag | 20260528 | 1048576 | `9226357cb0a544a6d3cb07546a7f35c15b0a2e33561e9ceb17a644642edcd22f` |
| Phase 4 projected bag | 20260529 | 524288 | `42e7bfa695cc080334cd8d51d4a9920784d90948343e8c73a9db55bd1beec6fa` |
| Phase 4 projected bag | 20260529 | 1048576 | `bc68f08df128608da747652472bb1b0b33019f3d759c3a6502f51d65436be411` |

Recommendation: no re-run required for comparability; phases are same protocol and deterministic same eval set per seed/horizon.
