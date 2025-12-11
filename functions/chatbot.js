const fetch = require("node-fetch");
const OpenAI = require("openai");

// --- Setup OpenAI client ---
const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// --- Setup Hotel API ---
const HOTEL_API_ENDPOINT = "https://hotel.dev-maister.gr/hotel_Casa/mcp_server/index.php";
const HOTEL_API_BEARER_TOKEN = process.env.HOTEL_API_BEARER_TOKEN;

// --- Helper functions for hotel API calls ---
async function getHotelAvailability({ json_key, start, end, adults, kids, minors }) {
  const headers = {
    Authorization: `Bearer ${HOTEL_API_BEARER_TOKEN}`,
    Accept: "*/*",
    "User-Agent": "Node.js"
  };
  const params = new URLSearchParams({ json_key, start, end, adults, kids, minors });
  try {
    const res = await fetch(`${HOTEL_API_ENDPOINT}?${params.toString()}`, { headers });
    const data = await res.json();
    return data;
  } catch (err) {
    return { error: "API call failed", details: err.message };
  }
}

async function getHotelPrice({ json_key, start, end, adults, kids, minors }) {
  const headers = {
    Authorization: `Bearer ${HOTEL_API_BEARER_TOKEN}`,
    Accept: "*/*",
    "User-Agent": "Node.js"
  };
  const params = new URLSearchParams({ json_key, start, end, adults, kids, minors });
  try {
    const res = await fetch(`${HOTEL_API_ENDPOINT}?${params.toString()}`, { headers });
    const data = await res.json();
    return data;
  } catch (err) {
    return { error: "API call failed", details: err.message };
  }
}

// --- Netlify function handler ---
exports.handler = async function(event, context) {
  try {
    const body = JSON.parse(event.body || "{}");
    const userMessage = body.message || "";
    const conversation = body.messages || []; // optional conversation memory

    // --- System prompt ---
    const systemPrompt = `
      You are a hotel reception assistant for Hotel Ilion.
      You can chat naturally with the user, ask clarifying questions, and only call 
      getHotelAvailability or getHotelPrice when you have check-in, check-out, and guests.
      Never reveal room names or numbers.
      Always clarify ages of children.
    `;

    // --- Messages for GPT ---
    const messages = [
      { role: "system", content: systemPrompt },
      ...conversation,
      { role: "user", content: userMessage }
    ];

    // --- GPT call with function definitions ---
    const tools = [
      {
        name: "getHotelAvailability",
        description: "Get hotel room availability for a given date range.",
        parameters: {
          type: "object",
          properties: {
            json_key: { type: "string" },
            start: { type: "string" },
            end: { type: "string" },
            adults: { type: "string" },
            kids: { type: "string" },
            minors: { type: "string" }
          },
          required: ["json_key", "start", "end", "adults", "kids", "minors"]
        }
      },
      {
        name: "getHotelPrice",
        description: "Get hotel room prices for a given date range.",
        parameters: {
          type: "object",
          properties: {
            json_key: { type: "string" },
            start: { type: "string" },
            end: { type: "string" },
            adults: { type: "string" },
            kids: { type: "string" },
            minors: { type: "string" }
          },
          required: ["json_key", "start", "end", "adults", "kids", "minors"]
        }
      }
    ];

    const gptResponse = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages,
      functions: tools,
      function_call: "auto"
    });

    let aiMsg = gptResponse.choices[0].message;

    // --- Handle function calls ---
    if (aiMsg.function_call) {
      const { name, arguments: argsStr } = aiMsg.function_call;
      const args = JSON.parse(argsStr || "{}");
      let result;

      if (name === "getHotelAvailability") {
        result = await getHotelAvailability(args);
      } else if (name === "getHotelPrice") {
        result = await getHotelPrice(args);
      } else {
        result = { error: "Unknown function call" };
      }

      // Append function response and get final GPT reply
      messages.push({ role: "assistant", content: null, function_call: aiMsg.function_call });
      messages.push({ role: "function", name, content: JSON.stringify(result) });

      const finalGpt = await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages,
        functions: tools
      });

      aiMsg = finalGpt.choices[0].message;
    }

    // --- Return response to frontend ---
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type"
      },
      body: JSON.stringify({
        response: aiMsg.content || "Hello! How can I assist you?",
        messages
      })
    };

  } catch (err) {
    return {
      statusCode: 500,
      headers: { "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ error: err.message })
    };
  }
};
