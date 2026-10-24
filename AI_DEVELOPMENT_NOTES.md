# AI Development Notes

## 1. AI Tools Used

- **ChatGPT:** Used as a development assistant for planning the architecture, understanding implementation approaches, troubleshooting errors, preparing tests, and documenting the project.
- **Groq API:** Integrated into the application to classify natural-language business questions into predefined analytics operations.
- **Visual Studio Code:** Used for implementation, debugging, and running the application and tests.

## 2. How AI Was Used

The AI classifier interprets a user's question and identifies the intended operation, such as total revenue, monthly revenue, top-performing product, regional performance, or month-to-month comparison.

The classifier returns a structured result rather than generating SQL. The backend validates the classification and passes supported operations to predefined analytics functions. This approach keeps database queries controlled and separates language interpretation from business calculations.

Deterministic rules are also used for supported question patterns, providing a fallback when AI classification is unavailable.

## 3. Challenges Encountered

### Dataset format and data quality

The supplied dataset was an Excel workbook (`.xlsx`), so the import process needed to support Excel instead of assuming the input was a CSV file. One completed transaction had a missing unit price, making its revenue uncalculable.

**Resolution:** The import process was checked against the source data, and the analytics logic excluded records with uncalculable revenue from revenue totals.

### AI model integration

The initial Groq model identifier returned a `NotFoundError`.

**Resolution:** The model configuration was updated to `openai/gpt-oss-120b`, and the classifier was tested again. The classifier subsequently returned the expected structured classification for a regional-performance question.

### Validation and reliability

Unsupported questions and invalid month inputs needed to be handled without causing unexpected application failures.

**Resolution:** Input validation and automated tests were added for analytics operations, empty questions, unsupported questions, invalid months, and comparisons with a zero baseline.

## 4. Debugging and Testing Approach

- Inspected the dataset structure, date range, transaction counts, and missing values.
- Rebuilt the SQLite database from the source workbook and checked the import summary.
- Used the FastAPI interactive documentation to test API endpoints and inspect responses.
- Tested the Groq classifier independently from the dashboard.
- Ran the analytics test suite with Pytest and verified that all nine tests passed.

## 5. Current Limitations

- Natural-language interpretation is limited to the supported analytics operations.
- AI classification requires a valid API key and network access.
- The dataset is relatively small and contains a record with missing revenue information.
- The current tests focus primarily on analytics and validation; additional API, UI, and AI-failure tests would improve coverage.

## 6. Improvements With More Development Time

1. Expand natural-language understanding and support more business questions.
2. Add filters for product category, sales channel, region, and date range.
3. Improve visualizations and allow users to export analytical results.
4. Add tests for API responses, database import edge cases, and AI failures.
5. Improve error messages, logging, and monitoring.
6. Add deployment configuration and more comprehensive setup documentation.

## 7. Key Learning

This project demonstrates how an AI language classifier can be combined with conventional backend analytics. AI interprets the user's intent, while validated application logic and predefined SQL queries perform the actual calculations. This separation improves control, reliability, and maintainability.
