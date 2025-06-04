"""This module provides a service for generating smart task suggestions
based on analysis of existing tasks."""

import re
import difflib
from typing import List
from collections import Counter, defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.task_repository import TaskRepository
from app.models.task import TaskSuggestion, TaskPublic, TaskStatus


class SmartSuggestionService:
    """
    Service for generating smart task suggestions based on analysis of existing tasks.

    This service analyzes task titles, completion sequences, and frequency patterns
    to generate relevant task suggestions.
    """

    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def generate_suggestions(
        self, session: AsyncSession, limit: int = 5
    ) -> List[TaskSuggestion]:
        """
        Generate a list of smart task suggestions based on analysis of existing tasks.

        Args:
            session: The SQLAlchemy AsyncSession for database access.
            limit: The maximum number of suggestions to return.

        Returns:
            A list of TaskSuggestion objects containing suggested tasks.
        """

        tasks = await self.task_repository.get_all_tasks_for_analysis(session)

        if len(tasks) < 2:
            return self._get_default_suggestions()

        suggestions = []

        pattern_suggestions = self._analyze_title_patterns(tasks)
        suggestions.extend(pattern_suggestions[:2])

        sequence_suggestions = self._analyze_completion_sequences(tasks)
        suggestions.extend(sequence_suggestions[:2])

        frequency_suggestions = self._analyze_frequency_patterns(tasks)
        suggestions.extend(frequency_suggestions[:2])

        suggestions.sort(key=lambda x: x.confidence_score, reverse=True)
        return suggestions[:limit]

    def _analyze_title_patterns(self, tasks: List[TaskPublic]) -> List[TaskSuggestion]:
        """
        Analyze task titles to find common patterns and generate suggestions.

        Args:
            tasks: List of TaskPublic objects to analyze.

        Returns:
            A list of TaskSuggestion objects based on frequent title words.
        """

        suggestions = []

        title_words = []
        for task in tasks:
            words = re.findall(r"\b\w+\b", task.title.lower())
            title_words.extend(words)

        stop_words = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        filtered_words = [
            word for word in title_words if word not in stop_words and len(word) > 2
        ]
        word_counts = Counter(filtered_words)

        for word, count in word_counts.most_common(3):
            if count >= 2:
                confidence = min(0.8, count / len(tasks) * 2)

                variations = [
                    f"{word.title()} Review",
                    f"{word.title()} Follow-up",
                    f"{word.title()} Planning",
                    f"Weekly {word.title()} Check",
                ]

                for variation in variations:
                    if not self._title_exists(tasks, variation):
                        suggestions.append(
                            TaskSuggestion(
                                suggested_title=variation,
                                confidence_score=confidence,
                                reasoning=(
                                    f"Based on frequent use of '{word}' in {count} existing tasks"
                                ),
                                suggested_description=(
                                    f"Follow-up task related to {word} activities"
                                ),
                            )
                        )
                        break

        return suggestions

    def _analyze_completion_sequences(
        self, tasks: List[TaskPublic]
    ) -> List[TaskSuggestion]:
        """
        Analyze completed tasks to detect follow-up patterns and generate suggestions.

        Args:
            tasks: List of TaskPublic objects to analyze.

        Returns:
            A list of TaskSuggestion objects based on completion sequences.
        """

        suggestions = []
        completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]

        if len(completed_tasks) < 2:
            return suggestions

        theme_groups = defaultdict(list)
        for task in completed_tasks:
            words = re.findall(r"\b\w+\b", task.title.lower())
            if words:
                theme = words[0]
                if len(theme) > 3:
                    theme_groups[theme].append(task)

        for theme, theme_tasks in theme_groups.items():
            if len(theme_tasks) >= 2:
                confidence = min(
                    0.9, len(theme_tasks) / len(completed_tasks) * 1.5
                )

                follow_up_suggestions = [
                    f"{theme.title()} Analysis and Review",
                    f"{theme.title()} Next Steps Planning",
                    f"{theme.title()} Progress Assessment",
                    f"{theme.title()} Optimization",
                ]

                for suggestion in follow_up_suggestions:
                    if not self._title_exists(tasks, suggestion):
                        suggestions.append(
                            TaskSuggestion(
                                suggested_title=suggestion,
                                confidence_score=confidence,
                                reasoning=(
                                    f"Follow-up pattern detected: "
                                    f"{len(theme_tasks)} completed tasks related to '{theme}'"
                                ),
                                suggested_description=(
                                    f"Next logical step after completing {theme}-related tasks"
                                ),
                            )
                        )
                        break

        return suggestions

    def _analyze_frequency_patterns(
        self, tasks: List[TaskPublic]
    ) -> List[TaskSuggestion]:
        """
        Analyze tasks for recurring patterns based on title similarity and generate suggestions.

        Args:
            tasks: List of TaskPublic objects to analyze.

        Returns:
            A list of TaskSuggestion objects based on frequency patterns.
        """

        suggestions = []

        title_groups = defaultdict(list)
        titles = [task.title.lower() for task in tasks]

        for i, title in enumerate(titles):
            for j, other_title in enumerate(titles[i + 1 :], i + 1):
                similarity = difflib.SequenceMatcher(None, title, other_title).ratio()
                if similarity > 0.6:
                    base_title = (
                        title if len(title) <= len(other_title) else other_title
                    )
                    title_groups[base_title].append(tasks[i])
                    title_groups[base_title].append(tasks[j])

        for base_title, similar_tasks in title_groups.items():
            if len(similar_tasks) >= 2:
                unique_tasks = list({task.id: task for task in similar_tasks}.values())
                confidence = min(
                    0.85, len(unique_tasks) / len(tasks) * 2
                )

                time_variations = [
                    f"Monthly {base_title.title()}",
                    f"Weekly {base_title.title()}",
                    f"{base_title.title()} - Next Quarter",
                    f"Annual {base_title.title()}",
                ]

                for variation in time_variations:
                    if not self._title_exists(tasks, variation):
                        suggestions.append(
                            TaskSuggestion(
                                suggested_title=variation,
                                confidence_score=confidence,
                                reasoning=(
                                    f"Recurring pattern detected: "
                                    f"{len(unique_tasks)} similar tasks found"
                                ),
                                suggested_description=(
                                    "Recurring task based on pattern analysis of similar activities"
                                ),
                            )
                        )
                        break

        return suggestions

    def _title_exists(self, tasks: List[TaskPublic], title: str) -> bool:
        """
        Check if a title already exists in the task list.

        Args:
            tasks: List of TaskPublic objects.
            title: The title to check for existence.

        Returns:
            True if the title exists, False otherwise.
        """

        return any(task.title.lower() == title.lower() for task in tasks)

    def _get_default_suggestions(self) -> List[TaskSuggestion]:
        """
        Provide default suggestions when insufficient data is available.

        Returns:
            A list of default TaskSuggestion objects.
        """

        return [
            TaskSuggestion(
                suggested_title="Weekly Planning Session",
                confidence_score=0.6,
                reasoning="Default suggestion for task organization",
                suggested_description="Plan and organize tasks for the upcoming week",
            ),
            TaskSuggestion(
                suggested_title="Progress Review Meeting",
                confidence_score=0.5,
                reasoning="Default suggestion for progress tracking",
                suggested_description="Review progress on current projects and tasks",
            ),
        ]
