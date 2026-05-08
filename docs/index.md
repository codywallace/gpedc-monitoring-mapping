# gpedc-monitoring-mapping — methodology

Methodology and reference documentation for the GPEDC × IATI mapping. The companion artefacts — the [`gpedc_iati_mapping.xlsx`](https://github.com/codywallace/gpedc-monitoring-mapping/blob/main/gpedc_iati_mapping.xlsx) workbook and the Plotly Dash web app under [`app/`](https://github.com/codywallace/gpedc-monitoring-mapping/tree/main/app) — render the same data; this documentation explains how that data is built.

If you are looking for the high-level project pitch, install instructions, or the public Python API, the [project README](https://github.com/codywallace/gpedc-monitoring-mapping#readme) is the right starting point. This site goes deeper on the *how*: which IATI elements feed which GPEDC indicators, what reporting-org readiness actually measures, and where the numbers come from.

```{toctree}
:maxdepth: 2
:caption: Methodology

methodology/overview
methodology/data-sources
methodology/pipeline
methodology/reporting-org-readiness
methodology/crs-iati-interoperability
methodology/untying-subcontracts
methodology/feasibility-categorisation
```

```{toctree}
:maxdepth: 1
:caption: Reference

api
references
```

## How the documentation is organised

::::{grid} 1 2 3 3
:gutter: 3

:::{grid-item-card} Methodology
:link: methodology/overview
:link-type: doc

Why this analysis exists, what each metric measures, and the design decisions behind the pipeline.
:::

:::{grid-item-card} Data sources
:link: methodology/data-sources
:link-type: doc

The IATI bulk-data service, the GPEDC official donor mapping, and the policy documents that anchor the mapping calls.
:::

:::{grid-item-card} Reporting-org readiness
:link: methodology/reporting-org-readiness
:link-type: doc

How the per-publisher coverage rates on the heatmap are computed — element-by-element.
:::

:::{grid-item-card} CRS × IATI interoperability
:link: methodology/crs-iati-interoperability
:link-type: doc

A1 / A2 / A9 `other-identifier` rates and the reconciliation tier classification.
:::

:::{grid-item-card} Untying & subcontracts
:link: methodology/untying-subcontracts
:link-type: doc

The `transaction/receiver-org/@ref` floor metric for the Tier-2 untying supplement.
:::

:::{grid-item-card} Feasibility categorisation
:link: methodology/feasibility-categorisation
:link-type: doc

How each GPEDC indicator was placed in one of the five feasibility buckets.
:::

::::
