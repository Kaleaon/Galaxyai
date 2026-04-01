# GalaxyAI Frontend

React + Vite UI for:

- Domain registration
- Fact ingestion with contradiction flagging
- Query results with confidence/state badges
- 3D map view powered by `GET /map3d`

## Development

```bash
cd app/frontend
npm install
cp .env.example .env
npm run dev
```

Set `VITE_API_MOCK_MODE=true` to use the built-in mock API while backend endpoints are unavailable.
