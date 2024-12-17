import json
import pytest
from model import LLMProvider
from utils.logger import log_evaluation
from httpx import AsyncClient
from app import app
from httpx import AsyncClient
from app import app
import asyncio
import time


def print_api_result(test_name, response):
    print(f"\n=== {test_name} API Response ===")
    print(f"Status Code: {response.status_code}")
    print("Response Data:")
    print(json.dumps(response.json(), indent=2))
    print("=" * 50)


@pytest.mark.asyncio
async def test_switch_to_groq(client):
    response = await client.post(
        "/set-provider",
        json={"provider": "groq"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully switched to groq"


@pytest.mark.asyncio
async def test_switch_to_ollama(client):
    response = await client.post(
        "/set-provider",
        json={"provider": "ollama"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully switched to ollama"


@pytest.mark.asyncio
async def test_invalid_provider(client):
    response = await client.post(
        "/set-provider",
        json={"provider": "invalid"}
    )
    assert response.status_code == 200
    assert "error" in response.json()


@pytest.mark.asyncio
async def test_scoring_endpoint(client, sample_answer):
    response = await client.post(
        "/score",
        json=sample_answer
    )
    result = response.json()
    log_evaluation(
        "API Scoring Endpoint",
        {"request": sample_answer, "status_code": response.status_code},
        result
    )
    print_api_result("Scoring Endpoint", response)
    assert response.status_code == 200

    result = response.json()
    assert "score" in result
    assert "reason" in result
    assert isinstance(result["score"], float)
    assert isinstance(result["reason"], str)
    assert 0 <= result["score"] <= sample_answer["total_score"]


@pytest.mark.asyncio
async def test_scoring_empty_answer(client, sample_answer):
    sample_answer["student_ans"] = ""
    response = await client.post(
        "/score",
        json=sample_answer
    )
    result = response.json()
    log_evaluation(
        "API Empty Answer",
        {"request": sample_answer, "status_code": response.status_code},
        result
    )
    print_api_result("Empty Answer", response)
    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 0
    assert isinstance(result["reason"], str)


@pytest.mark.asyncio
async def test_scoring_with_question(client, sample_answer):
    sample_answer["question"] = "Explain the process of photosynthesis."
    response = await client.post(
        "/score",
        json=sample_answer
    )
    print_api_result("Score With Question", response)
    assert response.status_code == 200

    result = response.json()
    assert "score" in result
    assert "reason" in result
    assert isinstance(result["score"], float)
    assert isinstance(result["reason"], str)


@pytest.mark.asyncio
async def test_scoring_without_question(client, sample_answer):
    if "question" in sample_answer:
        del sample_answer["question"]
    response = await client.post(
        "/score",
        json=sample_answer
    )
    assert response.status_code == 200

    result = response.json()
    assert "score" in result
    assert "reason" in result


@pytest.mark.asyncio
async def test_scoring_with_guidelines(client, sample_answer):
    sample_answer["guidelines"] = "Focus on technical accuracy and completeness"
    response = await client.post(
        "/score",
        json=sample_answer
    )
    result = response.json()
    log_evaluation(
        "API Scoring With Guidelines",
        {"request": sample_answer, "status_code": response.status_code},
        result
    )
    print_api_result("Score With Guidelines", response)
    assert response.status_code == 200
    assert "score" in result
    assert "reason" in result
    assert isinstance(result["score"], float)
    assert isinstance(result["reason"], str)


@pytest.mark.asyncio
async def test_scoring_with_empty_guidelines(client, sample_answer):
    sample_answer["guidelines"] = ""
    response = await client.post(
        "/score",
        json=sample_answer
    )
    result = response.json()
    log_evaluation(
        "API Scoring With Empty Guidelines",
        {"request": sample_answer, "status_code": response.status_code},
        result
    )
    print_api_result("Score With Empty Guidelines", response)
    assert response.status_code == 200
    assert "score" in result
    assert "reason" in result
    assert isinstance(result["score"], float)
    assert isinstance(result["reason"], str)


@pytest.mark.asyncio
async def test_concurrent_vs_sequential_scoring(client, sample_answer):
    # Prepare two different questions
    first_query = sample_answer.copy()
    second_query = sample_answer.copy()
    second_query["question"] = "What is cellular respiration?"
    second_query["expected_ans"] = "Cellular respiration is the process by which cells break down glucose to produce ATP, using oxygen and releasing carbon dioxide and water."
    
    # Test sequential execution
    start_time = time.time()
    response1 = await client.post("/score", json=first_query)
    response2 = await client.post("/score", json=second_query)
    sequential_time = time.time() - start_time
    
    # Test concurrent execution
    start_time = time.time()
    responses = await asyncio.gather(
        client.post("/score", json=first_query),
        client.post("/score", json=second_query)
    )
    concurrent_time = time.time() - start_time
    
    # Log results
    log_evaluation(
        "Performance Comparison",
        {
            "sequential_time": sequential_time,
            "concurrent_time": concurrent_time,
            "improvement": f"{(sequential_time - concurrent_time) / sequential_time * 100:.2f}%"
        },
        {"status": "completed"}
    )
    
    print(f"\n=== Performance Test Results ===")
    print(f"Sequential Time: {sequential_time:.2f}s")
    print(f"Concurrent Time: {concurrent_time:.2f}s")
    print(f"Improvement: {(sequential_time - concurrent_time) / sequential_time * 100:.2f}%")
    print("=" * 50)
    
    # Verify responses
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert responses[0].status_code == 200
    assert responses[1].status_code == 200
    
    # Verify concurrent execution was faster
    assert concurrent_time < sequential_time, "Concurrent execution should be faster than sequential"
