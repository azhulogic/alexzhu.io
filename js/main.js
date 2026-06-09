const words = [
  "engineer.",
  "developer.",
  "pilot.",
  "solver.",
  "pianist.",
  "traveler.",
  "climber."
];

const typedWord = document.getElementById("typed-word");

if (typedWord) {
  let wordIndex = 0;
  let letterIndex = 0;
  let isDeleting = false;

  const typingSpeed = 90;
  const deletingSpeed = 45;
  const pauseAfterTyping = 3000;
  const pauseAfterDeleting = 300;

  function typeLoop() {
    const currentWord = words[wordIndex];

    if (isDeleting) {
      letterIndex--;
    } else {
      letterIndex++;
    }

    typedWord.textContent = currentWord.substring(0, letterIndex);

    let delay = isDeleting ? deletingSpeed : typingSpeed;

    if (!isDeleting && letterIndex === currentWord.length) {
      delay = pauseAfterTyping;
      isDeleting = true;
    }

    if (isDeleting && letterIndex === 0) {
      isDeleting = false;
      wordIndex = (wordIndex + 1) % words.length;
      delay = pauseAfterDeleting;
    }

    setTimeout(typeLoop, delay);
  }

  typeLoop();
}
