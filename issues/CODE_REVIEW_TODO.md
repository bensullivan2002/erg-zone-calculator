# Code Review TODO List - ERG Zone Calculator

## 🏗️ Domain Models & Business Logic

### ✅ Completed
- [x] Constants organization improved (app/src/constants.py:7-18)

### 🔧 TODO Items

#### Zone Validation Enhancement
- [ ] Extract validation logic from `Zone.__post_init__` into separate methods (app/src/domain/domain_models.py:26-42)
  ```python
  def _validate_coefficients(self) -> None:
      validators = [
          self._validate_name,
          self._validate_coefficient_values,
          self._validate_coefficient_ordering
      ]
      for validator in validators:
          validator()
  ```

#### Constants Usage Updates
- [ ] Update all imports to use new `HeartRateValidation` and `PaceValidation` classes
  - [ ] Update `app/src/domain/domain_models.py` imports
  - [ ] Update `app/src/api/models.py` imports
  - [ ] Update any test files using the old constants

---

## 🚀 API Layer & FastAPI Implementation

### 🔧 TODO Items

#### Dependency Injection Implementation
- [ ] Add FastAPI dependency injection for better testability (app/src/api/app.py:79-131)
  ```python
  @lru_cache()
  def get_zone_config(config_path: str) -> ZoneConfig:
      return ZoneConfig(config_path)

  def get_hr_calculator(config: ZoneConfig = Depends(get_zone_config)) -> HRZoneCalculator:
      return HRZoneCalculator(config)
  ```

#### Response Model Enhancement
- [ ] Add metadata to response models (app/src/api/models.py:84-106)
  - [ ] Add `calculation_timestamp: datetime`
  - [ ] Add `config_version: str` to track which config was used

#### Custom Exception Hierarchy
- [ ] Create custom exception hierarchy for better error handling
  ```python
  class ZoneCalculatorError(Exception):
      """Base exception for zone calculator errors."""
      pass

  class ConfigurationError(ZoneCalculatorError):
      """Raised when configuration is invalid."""
      pass

  class ValidationError(ZoneCalculatorError):
      """Raised when input validation fails."""
      pass
  ```

---

## 🧪 Test Coverage & Quality

### 🔧 TODO Items

#### Test Organization
- [ ] Remove `sys.path` manipulation from individual test files (app/tests/test_zone_calculators.py:10-12)
- [ ] Add proper package structure in `conftest.py`

#### Property-Based Testing
- [ ] Add hypothesis tests for more robust validation
  ```python
  from hypothesis import given, strategies as st

  @given(st.integers(min_value=100, max_value=240))
  def test_hr_benchmark_always_valid(max_hr):
      benchmark = HRBenchmark(max_hr=max_hr)
      assert benchmark.max_hr == max_hr
  ```

#### Performance Testing
- [ ] Add benchmarks for calculator performance
  ```python
  def test_calculator_performance(benchmark):
      """Ensure calculations complete within acceptable time."""
      import time
      start = time.time()
      calculator.calculate_all_lower_bounds(180)
      assert time.time() - start < 0.1  # 100ms max
  ```

---

## ☁️ Infrastructure & Deployment

### 🔧 TODO Items

#### Security Hardening
- [ ] Improve CORS configuration (infra/src/constructs/api_construct.py:61-66)
  ```python
  cors_preflight={
      "allow_origins": constants.ALLOW_ORIGINS,  # Don't use "*" in production
      "allow_methods": [apigwv2.CorsHttpMethod.GET, apigwv2.CorsHttpMethod.POST],
      "allow_headers": ["Content-Type"],  # Remove Authorization if not used
      "max_age": Duration.hours(1),  # Add cache control
  }
  ```

#### Monitoring & Observability
- [ ] Add CloudWatch alarms for API Gateway and Lambda
- [ ] Enable X-Ray tracing for Lambda function
  ```python
  self.lambda_function = lambda_.Function(
      # ... existing config
      tracing=lambda_.Tracing.ACTIVE,
      environment={
          "PYTHONPATH": constants.PYTHONPATH,
          "_X_AMZN_TRACE_ID": ""  # Enable X-Ray
      }
  )
  ```

#### Cost Optimization
- [ ] Consider Lambda provisioned concurrency for consistent performance
  ```python
  version = self.lambda_function.current_version
  alias = lambda_.Alias(self, "LiveAlias", alias_name="live", version=version)
  alias.add_provisioned_concurrency_config(
      "ProvisionedConfig",
      provisioned_concurrent_executions=2
  )
  ```

---

## 🎯 Architecture & Design Patterns

### 🔧 TODO Items

#### Configuration Management
- [ ] Implement environment-specific configurations
- [ ] Add configuration validation at startup
- [ ] Consider hot-reloading capabilities for config changes

#### Caching Strategy
- [ ] Add caching for frequently accessed configurations
  ```python
  from functools import lru_cache

  class CachedZoneConfig:
      def __init__(self, config_path: str):
          self.config_path = config_path
          self._config = ZoneConfig(config_path)

      @lru_cache(maxsize=128)
      def get_zone_bounds(self, zone_name: str, benchmark_key: str) -> tuple:
          # Cache expensive calculations
          pass
  ```

#### Plugin Architecture
- [ ] Make formatters pluggable
  ```python
  class FormatterRegistry:
      _formatters: Dict[str, Type[ZoneFormatter]] = {}

      @classmethod
      def register(cls, name: str, formatter_class: Type[ZoneFormatter]):
          cls._formatters[name] = formatter_class

      @classmethod
      def get_formatter(cls, name: str) -> ZoneFormatter:
          return cls._formatters[name]()
  ```

---

## 🚀 Production Readiness Checklist

### Immediate Priorities (High Impact, Low Effort)
- [ ] Add structured logging with correlation IDs
- [ ] Implement rate limiting to prevent abuse
- [ ] Add health check dependencies (database, external services)
- [ ] Configure log retention and monitoring alerts

### Medium-term Enhancements (High Impact, Medium Effort)
- [ ] API versioning strategy for future changes
- [ ] Request/response compression for better performance
- [ ] Database backend for configuration storage
- [ ] Authentication/authorization if needed

### Long-term Considerations (High Impact, High Effort)
- [ ] Multi-region deployment for global availability
- [ ] Event-driven architecture for real-time updates
- [ ] Machine learning integration for personalized zone recommendations

---

## 📝 Notes

### Areas of Excellence
- Excellent domain-driven design with clear separation of concerns
- Comprehensive test coverage with good edge case handling
- Well-structured API with proper validation and error handling
- Professional infrastructure setup with AWS CDK

### Priority Order
1. **Fix constants imports** (breaking changes due to refactoring)
2. **Add structured logging and monitoring** (production readiness)
3. **Implement dependency injection** (code quality)
4. **Add custom exception hierarchy** (error handling)
5. **Security hardening** (production security)

### Estimated Effort
- **High Priority Items**: 1-2 days
- **Medium Priority Items**: 1-2 weeks
- **Long-term Items**: 1-3 months

---

*Generated from comprehensive code review by Distinguished Engineer*