document.addEventListener("DOMContentLoaded", function () {
  const themeToggle = document.getElementById("theme-toggle");
  const htmlElement = document.documentElement;

  // ローカルストレージの値を取得
  let theme = localStorage.getItem("theme");

  // 初回ロード時のテーマ適用
  if (theme === "dark") {
      htmlElement.classList.add("dark");
      themeToggle.textContent = "☀️"; // ライトモードに切り替え
  } else {
      htmlElement.classList.remove("dark");
      themeToggle.textContent = "🌙"; // ダークモードに切り替え
  }

  // ボタンクリックでダークモード切り替え
  themeToggle.addEventListener("click", function () {
      if (htmlElement.classList.contains("dark")) {
          htmlElement.classList.remove("dark");
          localStorage.setItem("theme", "light");
          themeToggle.textContent = "🌙";
      } else {
          htmlElement.classList.add("dark");
          localStorage.setItem("theme", "dark");
          themeToggle.textContent = "☀️";
      }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const mainContent = document.querySelector("main");

  // アニメーションを手動で適用
  mainContent.style.opacity = 0;
  mainContent.style.transform = "translateY(-20px)";
  setTimeout(() => {
      mainContent.style.transition = "opacity 0.5s ease-in-out, transform 0.5s ease-in-out";
      mainContent.style.opacity = 1;
      mainContent.style.transform = "translateY(0)";
  }, 100);
});

document.addEventListener("DOMContentLoaded", function () {
  const flashMessage = document.querySelector(".mt-4.p-3");
  if (flashMessage) {
      setTimeout(() => {
          flashMessage.style.opacity = "0";
          flashMessage.style.transition = "opacity 0.5s ease-out";
      }, 3000);
  }
});
