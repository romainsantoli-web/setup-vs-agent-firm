# Benchmarks

Measures performance of the Firm Ecosystem's core operations.

## Quick start

```bash
python -m benchmarks.run                # All benchmarks
python -m benchmarks.run --only memory  # Memory operations only
python -m benchmarks.run --only tools   # Tool execution only
python -m benchmarks.run --json         # Machine-readable output
```

## Benchmarks

### Memory (4 benchmarks)

| Benchmark | What it measures |
|-----------|-----------------|
| `layer2_parsing` | Parse 50 weighted rules from CLAUDE.md (file I/O + regex) |
| `hebbian_weight_update` | Hebbian formula on 200 rules (vectorized computation) |
| `pii_regex_scan` | 5 PII regex patterns against a 50KB session log |
| `cosine_search_1k_768d` | Brute-force cosine similarity on 1000×768-dim vectors |

### Tools (4 benchmarks)

| Benchmark | What it measures |
|-----------|-----------------|
| `pydantic_validation` | Validate tool input with Pydantic v2 |
| `json_rpc_parse` | Parse a JSON-RPC tools/call request |
| `tool_registry_lookup` | Dict-based O(1) tool lookup in 150-tool registry |
| `config_load_json` | Load and parse a JSON configuration file |

## Comparison targets

These benchmarks establish baselines for comparison with:
- **mem0** — memory retrieval latency
- **Zep** — session memory lookup
- **LangGraph** — state checkpoint read/write

## CI Integration

Add to your workflow:

```yaml
- name: Run benchmarks
  run: python -m benchmarks.run --json > benchmark-results.json
```
