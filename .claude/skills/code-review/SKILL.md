# Code Review Skill

Review Python code for the AI Check project, focusing on code quality, security, performance, and maintainability.

## Trigger

Use this skill when:
- Reviewing pull requests
- Checking code before commit
- Analyzing code for improvements
- Looking for potential bugs or issues

## Instructions

When reviewing code, check the following aspects:

### 1. Code Quality

- **Naming**: Variables, functions, and classes follow naming conventions
  - snake_case for functions/variables
  - PascalCase for classes
  - UPPER_SNAKE_CASE for constants

- **Type Annotations**: All public functions have type hints
  ```python
  def process(image: np.ndarray, threshold: float = 0.5) -> DetectionResult:
  ```

- **Docstrings**: Public APIs have Google-style docstrings
  ```python
  def detect(self, image: ImageInfo) -> DetectionResult:
      """Detect anomalies in the image.

      Args:
          image: The image to analyze.

      Returns:
          Detection result with anomaly status and confidence.
      """
  ```

- **Code Complexity**: Functions are not too long (< 50 lines preferred)
- **DRY**: No duplicated code blocks

### 2. Security

- No hardcoded credentials or API keys
- File paths are validated (no path traversal)
- User inputs are sanitized
- No SQL injection vulnerabilities

### 3. Performance

- No unnecessary loops that could be vectorized
- Large objects are released after use
- Batch processing uses appropriate batch sizes
- GPU memory is managed properly

### 4. PyQt Specific

- Long operations use QThread, not main thread
- Signals/slots are properly connected
- UI updates happen on main thread
- Resources are properly cleaned up

### 5. Testing

- New code has corresponding tests
- Edge cases are covered
- Mocks are used appropriately

## Example Usage

```
Review the code in ai_check/detectors/forgery/ps_detector.py for:
1. Code quality issues
2. Performance improvements
3. PyQt thread safety
4. Missing type hints
```

## Output Format

```markdown
## Code Review: [filename]

### Summary
[Brief overall assessment]

### Issues Found

#### Critical
- [ ] [Description of critical issue] (line X)

#### Warning
- [ ] [Description of warning] (line X)

#### Suggestion
- [ ] [Description of suggestion] (line X)

### Positive Points
- [What's done well]

### Recommended Changes
```python
# [Specific code suggestions]
```
```
