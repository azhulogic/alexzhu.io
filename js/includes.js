async function includeHTML(selector, file) {
  const element = document.querySelector(selector);

  if (!element) {
    return;
  }

  const response = await fetch(file);

  if (!response.ok) {
    throw new Error(`Could not load ${file}`);
  }

  element.innerHTML = await response.text();
}

includeHTML("[data-include='header']", "partials/header.html");
includeHTML("[data-include='footer']", "partials/footer.html");