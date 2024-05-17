document.addEventListener("DOMContentLoaded", () => {
  document
    .getElementById("emailForm")
    .addEventListener("submit", async (event) => {
      event.preventDefault();

      const selectedEmails = Array.from(
        document.querySelectorAll(
          '#mailingListForm tbody input[type="checkbox"][name="email"]:checked'
        )
      ).map((input) => input.value);

      const subject = document.getElementById("subjectInput").value;
      const htmlContent = document.getElementById("htmlInput").value;
      const pureTextContent = document.getElementById("pureTextInput").value;

      const dataToSend = {
        emails: selectedEmails,
        mail: {
          text: pureTextContent,
          message: "Test",
          subject: subject,
          html_message: htmlContent,
        },
      };

      console.log(dataToSend);

      try {
        const response = await fetch(sendMailingUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(dataToSend),
        });

        if (response.ok) {
          alert("Письма успешно отправлены.");
        } else {
          alert("Ошибка отправки. Статус: " + response.status);
        }
      } catch (error) {
        alert("Ошибка отправки: " + error.message);
      }
    });
});


document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("selectAll").addEventListener("click", () => {
    const checkboxes = document.querySelectorAll(
      '#mailingListForm tbody input[type="checkbox"][name="email"]'
    );
    const isChecked = [...checkboxes].every((checkbox) => checkbox.checked);
    checkboxes.forEach((checkbox) => {
      checkbox.checked = !isChecked;
    });
  });
});
