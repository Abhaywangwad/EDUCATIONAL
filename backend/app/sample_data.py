from collections.abc import Sequence


DEMO_TEACHER: dict = {
    "id": "teacher-priya",
    "full_name": "Priya Raman",
    "role": "teacher",
}


DEMO_STUDENTS: Sequence[dict] = (
    {
        "id": "student-aarav",
        "full_name": "Aarav Sharma",
        "grade_level": "Grade 11",
        "parent_ids": ["parent-nandini"],
    },
    {
        "id": "student-meera",
        "full_name": "Meera Iyer",
        "grade_level": "Grade 11",
        "parent_ids": ["parent-raghav"],
    },
    {
        "id": "student-isha",
        "full_name": "Isha Menon",
        "grade_level": "Grade 10",
        "parent_ids": ["parent-kavya"],
    },
)


DEMO_PARENTS: Sequence[dict] = (
    {
        "id": "parent-nandini",
        "full_name": "Nandini Sharma",
        "child_ids": ["student-aarav"],
    },
    {
        "id": "parent-raghav",
        "full_name": "Raghav Iyer",
        "child_ids": ["student-meera"],
    },
    {
        "id": "parent-kavya",
        "full_name": "Kavya Menon",
        "child_ids": ["student-isha"],
    },
)


DEMO_QUESTIONS: Sequence[dict] = (
    {
        "id": "q-data-vs-information",
        "question_text": "What is the difference between data and information?",
        "model_answer": (
            "Data is a collection of raw facts or observations. Information is processed, "
            "organized, and meaningful data that can support decisions."
        ),
        "expected_concepts": [
            "raw facts",
            "processed data",
            "meaningful output",
            "decision making",
        ],
        "synonyms": {
            "raw facts": ["unprocessed facts", "basic facts"],
            "processed data": ["organized data", "refined data"],
            "decision making": ["decision support", "making decisions"],
        },
        "weights": {
            "keyword_coverage": 0.3,
            "grammar_readability": 0.2,
            "facts_understanding": 0.5,
        },
    },
    {
        "id": "q-os-process-vs-thread",
        "question_text": "Explain the difference between a process and a thread.",
        "model_answer": (
            "A process is an independent program in execution with its own memory space. "
            "A thread is a smaller unit of execution within a process that shares the same memory. "
            "Threads are lighter and better for concurrent work inside one process."
        ),
        "expected_concepts": [
            "independent execution",
            "own memory space",
            "shared memory",
            "lightweight concurrency",
        ],
        "synonyms": {
            "independent execution": ["separate program", "separate running program"],
            "shared memory": ["common memory", "same memory"],
        },
        "weights": {
            "keyword_coverage": 0.3,
            "grammar_readability": 0.2,
            "facts_understanding": 0.5,
        },
    },
    {
        "id": "q-dbms-normalization",
        "question_text": "Why is normalization important in DBMS?",
        "model_answer": (
            "Normalization organizes database tables to reduce redundancy and dependency. "
            "It improves data consistency, prevents update anomalies, and makes the database easier to maintain."
        ),
        "expected_concepts": [
            "reduce redundancy",
            "data consistency",
            "prevent anomalies",
            "easy maintenance",
        ],
        "synonyms": {
            "prevent anomalies": ["avoid anomalies", "stop update anomalies"],
            "easy maintenance": ["simpler maintenance", "better maintenance"],
        },
        "weights": {
            "keyword_coverage": 0.3,
            "grammar_readability": 0.2,
            "facts_understanding": 0.5,
        },
    },
)


DEMO_ASSIGNMENTS: Sequence[dict] = (
    {
        "id": "assignment-aarav-process",
        "question_id": "q-os-process-vs-thread",
        "student_id": "student-aarav",
        "instructions": (
            "Write 90 to 140 words. Compare both concepts clearly and include one reason "
            "why threads are useful."
        ),
        "due_label": "Today, 5:00 PM",
        "duration_minutes": 20,
    },
    {
        "id": "assignment-meera-dbms",
        "question_id": "q-dbms-normalization",
        "student_id": "student-meera",
        "instructions": (
            "Write a structured answer in your own words. Mention redundancy, consistency, "
            "and anomalies."
        ),
        "due_label": "Tomorrow, 9:30 AM",
        "duration_minutes": 25,
    },
    {
        "id": "assignment-isha-data",
        "question_id": "q-data-vs-information",
        "student_id": "student-isha",
        "instructions": (
            "Use one short real-world example to show how raw data becomes useful information."
        ),
        "due_label": "Friday, 4:00 PM",
        "duration_minutes": 15,
    },
)


DEMO_CASES: Sequence[dict] = (
    {
        "id": "case-data-shallow",
        "question_id": "q-data-vs-information",
        "label": "Shallow definition",
        "category": "surface",
        "expected_outcome": "Should score lower than the deep explanation because it is correct but not detailed.",
        "student_answer": "Data is facts. Information is processed data.",
    },
    {
        "id": "case-data-deep",
        "question_id": "q-data-vs-information",
        "label": "Deep conceptual answer",
        "category": "deep",
        "expected_outcome": "Should score higher because it explains transformation and decision value.",
        "student_answer": (
            "Data is raw and unorganized facts, such as marks entered into a system. "
            "Information is produced when that data is processed and arranged so it becomes meaningful. "
            "For example, average marks or topper lists help in decision making, while raw marks alone do not."
        ),
    },
    {
        "id": "case-data-paraphrase",
        "question_id": "q-data-vs-information",
        "label": "Paraphrased correct answer",
        "category": "paraphrase",
        "expected_outcome": "Should still score well because the meaning matches even with different words.",
        "student_answer": (
            "Data is the original input we collect from the real world. "
            "Information is the useful meaning we get after arranging and analyzing that input."
        ),
    },
    {
        "id": "case-data-offtopic",
        "question_id": "q-data-vs-information",
        "label": "Off-topic answer",
        "category": "off-topic",
        "expected_outcome": "Should score near zero because it does not answer the question.",
        "student_answer": "A computer has input devices, output devices, memory, and a CPU.",
    },
    {
        "id": "case-thread-keywords",
        "question_id": "q-os-process-vs-thread",
        "label": "Keyword-heavy weak answer",
        "category": "surface",
        "expected_outcome": "Should not beat the deep answer because it lists terms without explanation.",
        "student_answer": (
            "Process, thread, memory, execution, concurrency, process, thread, shared memory, own memory."
        ),
    },
    {
        "id": "case-thread-deep",
        "question_id": "q-os-process-vs-thread",
        "label": "Deep comparison answer",
        "category": "deep",
        "expected_outcome": "Should score highest because it compares memory, isolation, and performance tradeoffs.",
        "student_answer": (
            "A process is an independent program with its own memory and resources, so one crashing process usually "
            "does not directly damage another. A thread is a smaller execution unit inside a process and shares that "
            "process memory, which makes thread creation faster but also requires careful coordination."
        ),
    },
    {
        "id": "case-thread-grammar",
        "question_id": "q-os-process-vs-thread",
        "label": "Correct but grammar-noisy",
        "category": "grammar",
        "expected_outcome": "Should stay fairly strong because grammar should reduce only one part of the score.",
        "student_answer": (
            "process have own memory space. thread share memory inside same process so it is lighter and fast for "
            "concurrent work."
        ),
    },
    {
        "id": "case-thread-offtopic",
        "question_id": "q-os-process-vs-thread",
        "label": "Irrelevant answer",
        "category": "off-topic",
        "expected_outcome": "Should score near zero.",
        "student_answer": "Normalization reduces redundancy in databases.",
    },
    {
        "id": "case-normalization-short",
        "question_id": "q-dbms-normalization",
        "label": "Short correct answer",
        "category": "short-correct",
        "expected_outcome": "Should beat long irrelevant text because it is still correct.",
        "student_answer": "Normalization reduces redundancy and keeps database data consistent.",
    },
    {
        "id": "case-normalization-deep",
        "question_id": "q-dbms-normalization",
        "label": "Deep analytical answer",
        "category": "deep",
        "expected_outcome": "Should score highest because it explains redundancy, anomalies, and maintenance.",
        "student_answer": (
            "Normalization is important because it organizes tables so duplicate data is reduced. "
            "That improves consistency and prevents update, insertion, and deletion anomalies. "
            "As a result, the database becomes easier to maintain and more reliable."
        ),
    },
    {
        "id": "case-normalization-long-irrelevant",
        "question_id": "q-dbms-normalization",
        "label": "Long but irrelevant answer",
        "category": "off-topic",
        "expected_outcome": "Should score lower than the short correct answer.",
        "student_answer": (
            "A database management system has many users and many features. "
            "It stores records, uses SQL, works with hardware, and can be part of many applications. "
            "DBMS is useful in banks, colleges, offices, and online systems."
        ),
    },
)
