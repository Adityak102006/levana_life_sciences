const MAX_LENGTHS = {
  name: 100,
  phone: 30,
  email: 254,
  message: 3000
};

module.exports = async function contact(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ success: false, message: "Method not allowed." });
  }

  let fields = req.body;
  if (typeof fields === "string") {
    try {
      fields = JSON.parse(fields);
    } catch {
      return res.status(400).json({ success: false, message: "Please check the form and try again." });
    }
  }
  if (!fields || typeof fields !== "object" || Array.isArray(fields)) {
    return res.status(400).json({ success: false, message: "Please check the form and try again." });
  }

  if (fields.botcheck) {
    return res.status(400).json({ success: false, message: "Please check the form and try again." });
  }

  const values = {};
  for (const [field, maxLength] of Object.entries(MAX_LENGTHS)) {
    const value = typeof fields[field] === "string" ? fields[field].trim() : "";
    if (value.length > maxLength) {
      return res.status(400).json({ success: false, message: "Please check the form and try again." });
    }
    values[field] = value;
  }

  if (!values.name || !values.phone || !values.message) {
    return res.status(400).json({ success: false, message: "Please complete the required fields." });
  }
  if (values.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    return res.status(400).json({ success: false, message: "Please enter a valid email address." });
  }

  const accessKey = process.env.WEB3FORMS_ACCESS_KEY;
  if (!accessKey) {
    console.error("WEB3FORMS_ACCESS_KEY is not configured.");
    return res.status(503).json({ success: false, message: "Contact form is temporarily unavailable." });
  }

  const payload = new URLSearchParams({
    access_key: accessKey,
    subject: "New contact message from Levana Life Sciences",
    from_name: values.name,
    name: values.name,
    phone: values.phone,
    message: values.message
  });
  if (values.email) payload.set("email", values.email);

  try {
    const upstream = await fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: payload,
      signal: AbortSignal.timeout(10000)
    });
    const result = await upstream.json();
    if (!upstream.ok || !result.success) {
      console.error("Web3Forms rejected a contact submission.", result.message || upstream.status);
      return res.status(502).json({ success: false, message: "Message could not be sent. Please try again." });
    }
    return res.status(200).json({ success: true });
  } catch (error) {
    console.error("Web3Forms contact submission failed.", error.message);
    return res.status(502).json({ success: false, message: "Message could not be sent. Please try again." });
  }
};
