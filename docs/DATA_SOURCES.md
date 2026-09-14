# Data and map sources

## World Bank indicators

The MVP uses the World Bank Indicators API for current-US-dollar GDP (`NY.GDP.MKTP.CD`), annual real GDP growth (`NY.GDP.MKTP.KD.ZG`), country metadata, and indicator definitions. The ingestion code records the request URL, retrieval timestamp, indicator definition, unit, year, and missing values.

- API guidance: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures
- Country metadata: https://datahelpdesk.worldbank.org/knowledgebase/articles/898590-country-api-queries
- Indicator metadata: https://datahelpdesk.worldbank.org/knowledgebase/articles/898599-indicator-api-queries

## World Bank reports

The MVP report catalog comes from the Documents & Reports API. Selected readable public reports provide the narrative evidence for document retrieval.

- API documentation: https://documents.worldbank.org/en/publication/documents-reports/api

Report metadata and source URLs are public evidence. A public listing does not automatically permit every form of redistribution, so the project records document-specific terms and does not publish raw reports until reviewed.

The first two reviewed report PDFs, their precise citations and licenses, and
the upload/indexing workflow are documented in [`corpus/README.md`](corpus/README.md).

## India boundary

Political maps of India use Survey of India published maps or digital boundary data as the standard. The project downloaded the official generalized 1:16 million outline vector from the Survey of India on 12 September 2026.

- Official source page: https://surveyofindia.gov.in/pages/outline-maps-of-india
- Government geospatial guidance: https://geospatial.dst.gov.in/Guidelines.aspx
- Downloaded source archive: `frontend/public/maps/survey-of-india-outline.zip`

Survey of India lists individual, internal, research, and website use among the permitted purposes for its outline vector, and prohibits commercial use. This portfolio must retain Survey of India attribution and must not be represented as a commercially reusable map asset. Before any commercial use or redistribution outside this project, the owner must review the current terms directly with Survey of India.

The rest of the world geometry is a separate map source. Rendering code must overlay the official Survey of India geometry for India rather than relying on the India outline in a generic world dataset.
