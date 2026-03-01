# File Location: /matrix/ai_models/ai_model_validator.py

import asyncio
import json
import re
from typing import Any

from matrix.ai_models.ai_model_manager import AiModelManager
from matrx_utils import vcprint


class AiModelValidator(AiModelManager):
    """Validates and fixes the integrity of AI model data entries."""

    async def validate_data_integrity(self) -> dict[str, list[str]]:
        """
        Orchestrates the validation of all AI model entries and returns a report of issues.
        """
        models = await self.load_all_models()
        validation_report = {
            "name_issues": [],
            "model_class_issues": [],
            "endpoint_issues": [],
            "model_provider_issues": [],
            "max_tokens_issues": [],  # New category
            "capabilities_issues": [],  # New category
        }

        model_names = {model.name for model in models}

        for model in models:
            name_issues = self._validate_name(model)
            class_issues = self._validate_model_class(model, model_names)
            endpoint_issues = self._validate_endpoints(model)
            provider_issues = self._validate_model_provider(model)
            max_tokens_issues = self._validate_max_tokens(model)
            capabilities_issues = self._validate_capabilities(model)

            model_identifier = f"Model '{model.name}' ({model.id})"
            if name_issues:
                validation_report["name_issues"].append(
                    f"{model_identifier}: {name_issues}"
                )
            if class_issues:
                validation_report["model_class_issues"].append(
                    f"{model_identifier}: {class_issues}"
                )
            if endpoint_issues:
                validation_report["endpoint_issues"].append(
                    f"{model_identifier}: {endpoint_issues}"
                )
                vcprint(
                    f"CRITICAL ENDPOINT ISSUE - {model_identifier}: {endpoint_issues}",
                    color="red",
                )
            if provider_issues:
                validation_report["model_provider_issues"].append(
                    f"{model_identifier}: {provider_issues}"
                )
            if max_tokens_issues:
                validation_report["max_tokens_issues"].append(
                    f"{model_identifier}: {max_tokens_issues}"
                )
            if capabilities_issues:
                validation_report["capabilities_issues"].append(
                    f"{model_identifier}: {capabilities_issues}"
                )

        self._print_validation_summary(validation_report)
        return validation_report

    async def fix_malformed_endpoints(self) -> dict[str, list[str]]:
        """
        Checks all models for malformed endpoints (strings that should be lists) and fixes them.
        Returns a report of fixes applied.
        """
        models = await self.load_all_models()
        fix_report = {"fixed": [], "skipped": [], "errors": []}

        for model in models:
            model_identifier = f"Model '{model.name}' ({model.id})"

            if not hasattr(model, "endpoints"):
                fix_report["skipped"].append(f"{model_identifier}: No endpoints field")
                continue

            endpoints = model.endpoints

            # If it's already a proper list of strings, skip
            if isinstance(endpoints, list) and all(
                isinstance(ep, str) for ep in endpoints
            ):
                fix_report["skipped"].append(
                    f"{model_identifier}: Endpoints already valid"
                )
                continue

            # If it's a string, try to fix it
            if isinstance(endpoints, str):
                try:
                    # Attempt to parse the string as JSON
                    parsed_endpoints = json.loads(endpoints)

                    # Ensure the parsed result is a list of strings
                    if not isinstance(parsed_endpoints, list):
                        fix_report["errors"].append(
                            f"{model_identifier}: Parsed endpoints is not a list"
                        )
                        continue

                    if not all(isinstance(ep, str) for ep in parsed_endpoints):
                        fix_report["errors"].append(
                            f"{model_identifier}: Parsed endpoints contains non-string elements"
                        )
                        continue

                    # Update the model with the fixed endpoints
                    await self.update_ai_model(model.id, endpoints=parsed_endpoints)
                    fix_report["fixed"].append(
                        f"{model_identifier}: Fixed endpoints from '{endpoints}' to {parsed_endpoints}"
                    )
                    vcprint(
                        f"FIXED - {model_identifier}: Converted endpoints to {parsed_endpoints}",
                        color="green",
                    )

                except json.JSONDecodeError:
                    fix_report["errors"].append(
                        f"{model_identifier}: Could not parse endpoints string '{endpoints}'"
                    )
                except Exception as e:
                    fix_report["errors"].append(
                        f"{model_identifier}: Error fixing endpoints - {str(e)}"
                    )
            else:
                fix_report["errors"].append(
                    f"{model_identifier}: Endpoints is neither a list nor a fixable string (type: {type(endpoints).__name__})"
                )

        # Print summary of fixes
        self._print_fix_summary(fix_report)
        return fix_report

    def _validate_name(self, model: Any) -> str:
        """Validates that the model name exists and contains only allowed characters."""
        if not hasattr(model, "name") or not model.name:
            return "Missing or empty name"

        name = model.name
        if not re.match(r"^[a-zA-Z0-9-:./]+$", name):
            return f"Invalid characters in name '{name}' (allowed: alphanumeric, -, :, /, .; no spaces)"
        if " " in name:
            return f"Spaces not allowed in name '{name}'"
        return ""

    def _validate_model_class(self, model: Any, existing_names: set) -> str:
        """Validates that model_class exists and matches an existing model name pattern."""
        if not hasattr(model, "model_class") or not model.model_class:
            return "Missing or empty model_class"

        model_class = model.model_class
        is_valid_class = any(name.startswith(model_class) for name in existing_names)
        if not is_valid_class:
            return f"Model class '{model_class}' doesn't match any existing model name pattern"
        return ""

    def _validate_endpoints(self, model: Any) -> str:
        """Validates that endpoints is a non-empty list of strings."""
        if not hasattr(model, "endpoints"):
            return "Missing endpoints field"

        endpoints = model.endpoints
        if not isinstance(endpoints, list):
            return f"Endpoints must be a list, got {type(endpoints).__name__}"

        if not endpoints:
            return "Endpoints list is empty"

        if not all(isinstance(ep, str) for ep in endpoints):
            return "All endpoints must be strings"

        return ""

    def _validate_model_provider(self, model: Any) -> str:
        """Validates that model_provider exists and is not empty."""
        if not hasattr(model, "model_provider") or not model.model_provider:
            return "Missing or empty model_provider"
        return ""

    def _validate_max_tokens(self, model: Any) -> str:
        """Validates that max_tokens exists and is a positive integer."""
        if not hasattr(model, "max_tokens"):
            return "Missing max_tokens field"

        max_tokens = model.max_tokens
        if max_tokens is None:
            return "max_tokens is None"
        if not isinstance(max_tokens, int):
            return f"max_tokens must be an integer, got {type(max_tokens).__name__}"
        if max_tokens <= 0:
            return f"max_tokens must be positive, got {max_tokens}"
        return ""

    def _validate_capabilities(self, model: Any) -> str:
        """Validates that capabilities exists and is non-empty."""
        if not hasattr(model, "capabilities"):
            return "Missing capabilities field"

        capabilities = model.capabilities
        if capabilities is None:
            return "capabilities is None"
        if not isinstance(capabilities, (dict, list)):
            return f"capabilities must be a dict or list, got {type(capabilities).__name__}"
        if not capabilities:
            return "capabilities is empty"
        return ""

    def _print_validation_summary(self, report: dict[str, list[str]]) -> None:
        """Prints a summary of all validation issues found."""
        total_issues = sum(len(issues) for issues in report.values())
        if total_issues == 0:
            vcprint(
                "Data integrity validation completed: No issues found", color="green"
            )
            return

        vcprint(
            f"Data integrity validation completed: Found {total_issues} issues",
            color="yellow",
        )
        for category, issues in report.items():
            if issues:
                vcprint(f"\n{category.replace('_', ' ').title()}:", color="yellow")
                for issue in issues:
                    vcprint(f"- {issue}", color="yellow")

    def _print_fix_summary(self, report: dict[str, list[str]]) -> None:
        """Prints a summary of all endpoint fixes applied."""
        total_fixed = len(report["fixed"])
        total_skipped = len(report["skipped"])
        total_errors = len(report["errors"])

        vcprint(
            f"Endpoint fix process completed: {total_fixed} fixed, {total_skipped} skipped, {total_errors} errors",
            color="blue",
        )
        if total_fixed > 0:
            vcprint("\nFixed:", color="green")
            for fix in report["fixed"]:
                vcprint(f"- {fix}", color="green")
        if total_errors > 0:
            vcprint("\nErrors:", color="red")
            for error in report["errors"]:
                vcprint(f"- {error}", color="red")


async def validate_and_fix_endpoints():
    validator = AiModelValidator()
    # Run validation first
    validation_report = await validator.validate_data_integrity()
    vcprint(
        data=validation_report, title="Validation Report", pretty=True, color="blue"
    )

    # Then run fixer
    fix_report = await validator.fix_malformed_endpoints()
    vcprint(data=fix_report, title="Fix Report", pretty=True, color="blue")


async def main():
    validator = AiModelValidator()
    validation_report = await validator.validate_data_integrity()
    vcprint(
        data=validation_report, title="Validation Report", pretty=True, color="blue"
    )


if __name__ == "__main__":
    import os

    os.system("cls")
    asyncio.run(validate_and_fix_endpoints())
