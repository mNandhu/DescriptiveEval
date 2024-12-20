import json
import pytest
from model import get_llm, LLMProvider, score
from utils.logger import log_evaluation


def print_result(test_name, result):
    print(f"\n=== {test_name} Output ===")
    print(f"Score: {result['score']}")
    print(f"Reason: {result['reason']}")
    print("=" * 50)


def test_llm_provider_switching():
    ollama_llm = get_llm(LLMProvider.OLLAMA)
    groq_llm = get_llm(LLMProvider.GROQ)
    assert ollama_llm != groq_llm


@pytest.mark.asyncio
async def test_score_calculation():
    llm = get_llm(LLMProvider.GROQ)
    params = {
        "student_ans": "Photosynthesis is the process where plants convert sunlight into energy.",
        "expected_ans": "Photosynthesis is the process by which plants convert light energy into chemical energy to produce glucose using carbon dioxide and water.",
        "total_score": 10
    }
    result = await score(llm=llm, **params)
    log_evaluation("Basic Score Calculation", params, result)
    print_result("Basic Score Calculation", result)
    assert isinstance(result["score"], float)
    assert isinstance(result["reason"], str)
    assert 0 <= result["score"] <= 10


@pytest.mark.asyncio
async def test_invalid_inputs():
    llm = get_llm(LLMProvider.GROQ)
    params = {
        "student_ans": "",
        "expected_ans": "",
        "total_score": -1
    }
    result = await score(llm=llm, **params)
    log_evaluation("Invalid Inputs", params, result)
    print_result("Invalid Inputs", result)
    assert result["score"] == 0
    assert isinstance(result["reason"], str)


@pytest.mark.asyncio
async def test_score_with_question():
    llm = get_llm(LLMProvider.GROQ)
    params = {
        "question": "Explain the process of photosynthesis.",
        "student_ans": "Photosynthesis is the process where plants convert sunlight into energy.",
        "expected_ans": "Photosynthesis is the process by which plants convert light energy into chemical energy to produce glucose using carbon dioxide and water.",
        "total_score": 10
    }
    result = await score(llm=llm, **params)
    log_evaluation("Score With Question", params, result)
    print_result("Score With Question", result)
    assert isinstance(result["score"], float)
    assert isinstance(result["reason"], str)
    assert 0 <= result["score"] <= 10


@pytest.mark.asyncio
async def test_score_with_guidelines():
    llm = get_llm(LLMProvider.GROQ)
    params = {
        "question": "Explain the process of photosynthesis.",
        "guidelines": "Evaluate based on: 1) Understanding of energy conversion 2) Mention of required materials 3) Accuracy of process description",
        "student_ans": "Photosynthesis is the process where plants convert sunlight into energy.",
        "expected_ans": "Photosynthesis is the process by which plants convert light energy into chemical energy to produce glucose using carbon dioxide and water.",
        "total_score": 10
    }
    result = await score(llm=llm, **params)
    log_evaluation("Score With Guidelines", params, result)
    print_result("Score With Guidelines", result)
    assert isinstance(result["score"], float)
    assert isinstance(result["reason"], str)
    assert 0 <= result["score"] <= 10


@pytest.mark.asyncio
async def test_score_with_question_and_guidelines():
    llm = get_llm(LLMProvider.GROQ)
    params = {
        "question": "Explain the process of photosynthesis.",
        "guidelines": "Focus on accuracy and completeness of the explanation.",
        "student_ans": "Photosynthesis is the process where plants convert sunlight into energy.",
        "expected_ans": "Photosynthesis is the process by which plants convert light energy into chemical energy to produce glucose using carbon dioxide and water.",
        "total_score": 10
    }
    result = await score(llm=llm, **params)
    log_evaluation("Score With Question and Guidelines", params, result)
    print_result("Score With Question and Guidelines", result)
    assert isinstance(result["score"], float)
    assert isinstance(result["reason"], str)
    assert 0 <= result["score"] <= 10


@pytest.mark.asyncio
async def test_rubic_and_breakdown():
    llm = get_llm(LLMProvider.GROQ)
    params = {
        "question": "Explain the process of photosynthesis.",
        "guidelines": "Focus on accuracy and completeness of the explanation.",
        "student_ans": "Photosynthesis is the process where plants convert sunlight into energy.",
        "expected_ans": "Photosynthesis is the process by which plants convert light energy into chemical energy to produce glucose using carbon dioxide and water.",
        "total_score": 10
    }
    result = await score(llm=llm, **params)
    log_evaluation("Score With Question and Guidelines", params, result)
    print_result("Score With Question and Guidelines", result)
    assert isinstance(result["score"], float)
    assert isinstance(result["reason"], str)
    assert 0 <= result["score"] <= 10
    assert "rubric" in result
    assert "breakdown" in result
    assert isinstance(result["rubric"], str)
    assert isinstance(result["breakdown"], str)
    assert len(result["rubric"]) > 0
    assert len(result["breakdown"]) > 0
