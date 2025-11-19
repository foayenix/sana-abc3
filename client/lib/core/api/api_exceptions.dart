/// Base API exception class
abstract class ApiException implements Exception {
  final String message;

  const ApiException(this.message);

  @override
  String toString() => message;
}

/// Network connectivity exception
class NetworkException extends ApiException {
  const NetworkException(super.message);
}

/// Request timeout exception
class TimeoutException extends ApiException {
  const TimeoutException(super.message);
}

/// Bad request (400) exception
class BadRequestException extends ApiException {
  const BadRequestException(super.message);
}

/// Unauthorized (401) exception
class UnauthorizedException extends ApiException {
  const UnauthorizedException(super.message);
}

/// Forbidden (403) exception
class ForbiddenException extends ApiException {
  const ForbiddenException(super.message);
}

/// Not found (404) exception
class NotFoundException extends ApiException {
  const NotFoundException(super.message);
}

/// Conflict (409) exception
class ConflictException extends ApiException {
  const ConflictException(super.message);
}

/// Validation (422) exception
class ValidationException extends ApiException {
  const ValidationException(super.message);
}

/// Rate limit (429) exception
class RateLimitException extends ApiException {
  const RateLimitException(super.message);
}

/// Server (5xx) exception
class ServerException extends ApiException {
  const ServerException(super.message);
}

/// Request cancelled exception
class RequestCancelledException extends ApiException {
  const RequestCancelledException(super.message);
}

/// Unknown exception
class UnknownException extends ApiException {
  const UnknownException(super.message);
}
