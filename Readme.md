# House of Paint (ЛКМщик)

## Preamble
This project was created during my early stages of learning IT, so the code may not be perfect.
If you'd like to contribute to the development of this project, we can start with refactoring. Please contact me, and I'll explain everything.

## Description
This application is designed for paint and coatings laboratories that use chemical raw materials to formulate paint recipes.
The application allows you to:
*   Keep track of reagents in the laboratory.
*   Create paint and coating formulations.
*   Store and visualize information about formulations.
*   Calculate parameters for single-component and two-component formulations.

You can check the source code for security and build the .exe file yourself.

## File Descriptions
*   `main.py`: The main file that initiates the application launch, registration, and password entry windows.
*   `projects.py`: The projects window, displaying a grid of formulations.
*   `recepture.py`: The specific formulation window, where formulations are created and edited.
*   `newReactives.py`: The window displaying a tabular list of reagents in the laboratory.
*   `component_card.py`: The window for adding new and editing existing reagents.
*   `activation.py`: Application activation logic (deprecated).
*   `database.py`: Handles database connection via SQLite.
*   `saves/`: Folder containing saved projects and formulations. The file structure mirrors the SQLite database.
*   `reactives.db`: SQLite database for reagents.

## Prerequisites
*   python 3.8.*
*   `pip install -r ./requirements.txt`

## Build Project to .exe
1.  Run the command:
    ```bash
    pyinstaller "./main.spec"
    ```
2.  An .exe file will appear in the `dist` folder.
3.  Take this .exe file and place it in a folder along with the other files from the repository: `reactives.db`, `import.xlsx`, `saves`, `media`, `backup`.

## Roadmap / To-Do (Priority Tasks)
*   Normalize data in the database.
*   Merge formulations and reagents into a single database.
*   Migrate to SQLAlchemy.

## Contributing
As mentioned, if you're interested in contributing, especially with refactoring, please reach out.

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

You are free to:

*   **Share** — copy and redistribute the material in any medium or format.
*   **Adapt** — remix, transform, and build upon the material.

Under the following terms:

*   **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
*   **NonCommercial** — You may not use the material for commercial purposes.
*   **No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

For the full license text, please visit: [https://creativecommons.org/licenses/by-nc/4.0/](https://creativecommons.org/licenses/by-nc/4.0/)

**In simple terms:** You are free to edit the code and use this application for any of your personal purposes. However, you are not permitted to sell the application itself or use it for other commercial purposes. If you share or adapt the code, you must provide appropriate credit to the original author(s) and indicate that it is licensed under CC BY-NC 4.0.