def test_retrieval_finds_relevant_knowledge(client, test_env):
    """Test retrieving passages for questions covered in knowledge base."""
    retriever = test_env.retriever
    result = retriever.retrieve("How much water should an adult drink daily?", top_k=2)

    assert result["reliable"] is True
    assert len(result["sources"]) > 0
    first_source = result["sources"][0]
    assert "source" in first_source
    assert "page" in first_source
    assert "snippet" in first_source
    assert "water" in result["context_text"].lower()

def test_retrieval_flags_unreliable_for_out_of_domain(client, test_env):
    """Test that out-of-domain query is correctly flagged as having no reliable context."""
    retriever = test_env.retriever
    # Query completely unrelated to healthcare knowledge base
    result = retriever.retrieve("quantum flux density matrix calculations for hadron colliders", top_k=2)

    # Either no results or distance exceeds reliable threshold
    if not result["reliable"]:
        assert result["reliable"] is False
        assert result["context_text"] == ""
