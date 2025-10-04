# Requirements Document

## Introduction

This feature involves creating a static website hosted on AWS S3 with CloudFront distribution that provides a rowing training zone calculator. The site will allow users to input either their 2000m rowing time or maximum heart rate and display corresponding training zones with heart rate ranges and pace targets. The calculator will use predefined zone configurations to compute personalized training metrics for rowing athletes.

## Requirements

### Requirement 1

**User Story:** As a rowing athlete, I want to input my 2000m time and see my training zones with corresponding heart rate ranges and pace targets, so that I can train effectively in different intensity zones.

#### Acceptance Criteria

1. WHEN a user enters a valid 2000m time in MM:SS format THEN the system SHALL display a table showing all training zones (UT3, UT2, UT1, AT, TR, AC, AP) with calculated heart rate ranges and pace per 500m
2. WHEN a user enters an invalid 2000m time format THEN the system SHALL display an error message indicating the correct format
3. WHEN the calculation is performed THEN the system SHALL use the zone multipliers from the pace_zones.json configuration file to calculate pace ranges
4. WHEN the calculation is performed THEN the system SHALL use the zone multipliers from the hr_zones.json configuration file to calculate heart rate ranges

### Requirement 2

**User Story:** As a rowing athlete, I want to input my maximum heart rate and see my training zones with corresponding heart rate ranges and pace targets, so that I can train using heart rate-based zone training.

#### Acceptance Criteria

1. WHEN a user enters a valid maximum heart rate (numeric value between 120-220) THEN the system SHALL display a table showing all training zones with calculated heart rate ranges and estimated pace per 500m
2. WHEN a user enters an invalid heart rate value THEN the system SHALL display an error message indicating the acceptable range
3. WHEN calculating from heart rate THEN the system SHALL use the hr_zones.json multipliers to determine heart rate ranges for each zone
4. WHEN calculating from heart rate THEN the system SHALL estimate pace zones using the relationship between heart rate and pace zones

### Requirement 3

**User Story:** As a user, I want a clean and intuitive interface that follows Material Design principles, so that the calculator is easy to use and visually appealing.

#### Acceptance Criteria

1. WHEN the page loads THEN the system SHALL display a clean, responsive interface with Material Design styling
2. WHEN viewing on mobile devices THEN the system SHALL maintain usability and readability across different screen sizes
3. WHEN interacting with form elements THEN the system SHALL provide clear visual feedback and follow Material Design input patterns
4. WHEN viewing results THEN the system SHALL display the zone table in a clear, organized format with appropriate typography and spacing

### Requirement 4

**User Story:** As a website visitor, I want the site to load quickly and be accessible from anywhere, so that I can use the calculator reliably.

#### Acceptance Criteria

1. WHEN the site is accessed THEN the system SHALL serve content from CloudFront CDN for fast global delivery
2. WHEN static assets are requested THEN the system SHALL serve them from S3 with appropriate caching headers
3. WHEN the page loads THEN the system SHALL be fully functional without requiring server-side processing
4. WHEN accessed via HTTPS THEN the system SHALL serve all content securely through CloudFront

### Requirement 5

**User Story:** As a developer, I want the site infrastructure to be defined as code, so that it can be deployed and managed consistently.

#### Acceptance Criteria

1. WHEN deploying the infrastructure THEN the system SHALL use AWS CDK to define S3 bucket and CloudFront distribution
2. WHEN the S3 bucket is created THEN the system SHALL be configured for static website hosting with appropriate permissions
3. WHEN the CloudFront distribution is created THEN the system SHALL be configured to serve the S3 content with appropriate caching policies
4. WHEN deploying THEN the system SHALL ensure the site is accessible via the CloudFront domain
