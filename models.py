def generate_response(results, model, tokenizer,value):
    prompt_text = " "
    for result in results:
        prompt_text += f"{result['label']}: {result['text']}\n"

    inputs = tokenizer(prompt_text, return_tensors="pt", max_length=1024, truncation=True)
    response = model.generate(inputs.input_ids, max_length=value)
    return response


def search_knowledge_graph(query, knowledge_graph):
    results = []
    query_words = query.lower().split()  # Split the query into individual words
    for entity, properties in knowledge_graph.items():
        entity_text = properties['text'].lower()
        # Check if any word in the query matches any word in the entity text, ignoring case
        if any(word in entity_text.lower().split() for word in query_words):
            results.append(properties)
    return results
