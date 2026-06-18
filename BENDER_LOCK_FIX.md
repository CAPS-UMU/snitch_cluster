# Bender.lock Fix — `make verilator` Failure

## Symptom

`make verilator` fails with one of:

```
%Error: verilator: No Input Verilog file specified on command line
make: *** No rule to make target 'target/sim/build/work-vlt/testharness.d'
```

## Root Cause

`Bender.lock` references commits that no longer exist on their remotes:

- **`axi`** (`colluca/axi.git`, `multicast` branch) — this branch was force-pushed and rebased. The locked commit (`bd1abffc...`) is permanently gone. The new commits on this branch require `common_cells v2-dev`, which renames all modules with a `cc_` prefix and is incompatible with the rest of the snitch RTL.
- **`idma`** — the `__deploy__bebefa3__master` deploy branch was pruned from the remote.

When bender can't check out these commits, it produces no stdout, leaving `testharness.f` as an empty file. Verilator then has no input files to compile.

## Fix

Replace `Bender.lock` with the one from the upstream `pulp-platform/snitch_cluster` project, which pins `axi` to a commit (`06410c36...`) that predates the incompatible rebase and is still fetchable by hash:

```bash
# From inside the container, at /repo
# 1. Fetch the missing axi commit into bender's local git cache
git -C .bender/git/db/axi-be603dd3cf4d91a4 fetch origin 06410c36819924e32db2afa428d244dbdbcd5d4e

# 2. Replace Bender.lock with the upstream version (see the file committed here)

# 3. Wipe stale checkouts and the empty file list
rm -rf .bender/git/checkouts/
rm -f target/sim/build/work-vlt/testharness.f

# 4. Build
make verilator
```

The working `Bender.lock` is the one now committed in this repo.

## Key commits in the working lock

| Package | Commit | Notes |
|---|---|---|
| `axi` | `06410c36` | Pre-rebase multicast branch; uses old `common_cells` API |
| `common_cells` | `ca9d577f` | `snitch` branch; no `cc_` module rename |
| `idma` | `28a36e5e` | `__deploy__b248755__master` (v0.6.5); still available |

## How to detect this problem in the future

```bash
bender script verilator -t rtl -t snitch_cluster -t snitch_cluster_wrapper -t verilator 2>&1 | grep "error:"
```

If bender prints `Failed to checkout commit ... not found`, the lock file has gone stale. Get a fresh `Bender.lock` from the upstream repo or fetch the specific commit hash directly as shown above.
