function addStepField() {
    const stepDescriptionInput = document.createElement("input");
    stepDescriptionInput.type = "text";
    stepDescriptionInput.name = "new_step_description";
    stepDescriptionInput.required = true;
    stepDescriptionInput.placeholder = "Опис кроку";
    stepDescriptionInput.className = "form-control";

    const removeButton = document.createElement("button");
    removeButton.textContent = "Вилучити";
    removeButton.className = "btn btn-secondary";

    const stepsDiv = document.getElementById("steps");
    const div = document.createElement("div");
    div.appendChild(stepDescriptionInput);
    div.appendChild(removeButton);
    div.className = "d-flex";
    stepsDiv.appendChild(div);

    removeButton.addEventListener("click", () => stepsDiv.removeChild(div));
}

function addIngredientField() {
    const nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.name = "new_ingredient_name";
    nameInput.required = true;
    nameInput.placeholder = "Назва інгредієнту";
    nameInput.className = "form-control";

    const volumeInput = document.createElement("input");
    volumeInput.type = "number";
    volumeInput.step = "0.001";
    volumeInput.name = "new_ingredient_volume";
    volumeInput.required = true;
    volumeInput.placeholder = "Обсяг";
    volumeInput.className = "form-control";

    const measureInput = document.createElement("input");
    measureInput.type = "text";
    measureInput.name = "new_ingredient_volume_measure";
    measureInput.required = true;
    measureInput.placeholder = "Міра обсягу";
    measureInput.className = "form-control";

    const removeButton = document.createElement("button");
    removeButton.textContent = "Вилучити";
    removeButton.className = "btn btn-secondary";

    const ingredientsDiv = document.getElementById("ingredients");
    const div = document.createElement("div");
    div.appendChild(nameInput);
    div.appendChild(volumeInput);
    div.appendChild(measureInput);
    div.appendChild(removeButton);
    div.className = "d-flex";
    ingredientsDiv.appendChild(div);

    removeButton.addEventListener("click", () => ingredientsDiv.removeChild(div));
}

function addTagField() {
    const input = document.createElement("input");
    input.type = "text";
    input.name = "new_tag_text";
    input.required = true;
    input.placeholder = "Тег";
    input.className = "form-control";

    const removeButton = document.createElement("button");
    removeButton.textContent = "Вилучити";
    removeButton.className = "btn btn-secondary";

    const tagsDiv = document.getElementById("tags");
    const div = document.createElement("div");
    div.appendChild(input);
    div.appendChild(removeButton);
    div.className = "d-flex";
    tagsDiv.appendChild(div);

    removeButton.addEventListener("click", () => tagsDiv.removeChild(div));
}

document.getElementById("add_step_button").addEventListener("click", addStepField);
document.getElementById("add_ingredient_button").addEventListener("click", addIngredientField);
document.getElementById("add_tag_button").addEventListener("click", addTagField);
