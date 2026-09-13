# Lead Generation & Website Audit Agent

A production-ready Python FastAPI application that finds local businesses, audits their websites for technical issues, classifies them as HOT or COLD leads, and stores the results in Google Sheets.

## Features
- **Serper API Integration**: Searches for local businesses by keyword and location.
- **Website Auditing**: Checks for SSL (HTTPS), Mobile Responsiveness (viewport meta tag), and Website Status (HTTP errors/timeouts).
- **Lead Qualification**: Automatically classifies leads as HOT (has issues) or COLD (no issues).
- **Google Sheets Sync**: Reads inputs and writes results to designated worksheets.
- **Rate Limiting & Safety**: Random delays between requests, robust error handling, and duplicate detection.

## Architecture
- **FastAPI**: Handles HTTP endpoints.
- **Services**: Modular classes for Serper, Website Auditing, Google Sheets, and Processing.
- **Models**: Pydantic models for strict data validation.
- **Utils**: Helpers for normalization, validation, and logging.

## Folder Structure