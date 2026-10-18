import { createSession, formatResults, isSearchable, submitAnswers, toQuery, waitForResults } from "./src/agent";

const incoming = "hey can you find me noise cancelling headphones";
const query = toQuery(incoming);
console.log("incoming:", incoming);
console.log("query:", query, "searchable:", isSearchable(query));

const { session_id } = await createSession(query, "sim");
console.log("session:", session_id);
await submitAnswers(session_id, [], true);
const snapshot = await waitForResults(session_id);
console.log("stage:", snapshot?.stage);
console.log("---\n" + formatResults(snapshot!));
