import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QComboBox, QMessageBox, QStackedWidget, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, QObject, QTimer, Qt
from qt_material import apply_stylesheet

# Контроллер игры: хранит состояние текущего вопроса, темы, вопросы и игроков
class GameController(QObject):
    update_player_state = pyqtSignal(dict)  # сигнал для оповещения окон об изменениях

    def __init__(self):
        super().__init__()
        self.state = {
            "current_topic": None,
            "current_question": None,
            "current_answer": None,
            "current_value": None,
            "show_answer": False,   # становится True при правильном ответе
            "incorrect": False      # True, если был неправильный ответ
        }
        self.topics = {
            "Тема 1": [
                {"question": "Вопрос 1", "answer": "Ответ 1", "value": 100, "used": False},
                {"question": "Вопрос 2", "answer": "Ответ 1", "value": 200, "used": False},
                {"question": "Вопрос 3", "answer": "Ответ 1", "value": 300, "used": False},
                {"question": "Вопрос 4", "answer": "Ответ 2", "value": 400, "used": False},
                {"question": "Вопрос 5", "answer": "Ответ 2", "value": 500, "used": False},
            ],
            "Тема 2": [
                {"question": "Вопрос 1", "answer": "Ответ 1", "value": 100, "used": False},
                {"question": "Вопрос 2", "answer": "Ответ 1", "value": 200, "used": False},
                {"question": "Вопрос 3", "answer": "Ответ 1", "value": 300, "used": False},
                {"question": "Вопрос 4", "answer": "Ответ 2", "value": 400, "used": False},
                {"question": "Вопрос 5", "answer": "Ответ 2", "value": 500, "used": False},
            ],
            "Тема 3": [
                {"question": "Вопрос 1", "answer": "Ответ 1", "value": 100, "used": False},
                {"question": "Вопрос 2", "answer": "Ответ 1", "value": 200, "used": False},
                {"question": "Вопрос 3", "answer": "Ответ 1", "value": 300, "used": False},
                {"question": "Вопрос 4", "answer": "Ответ 2", "value": 400, "used": False},
                {"question": "Вопрос 5", "answer": "Ответ 2", "value": 500, "used": False},
            ],
            "Тема 4": [
                {"question": "Вопрос 1", "answer": "Ответ 1", "value": 100, "used": False},
                {"question": "Вопрос 2", "answer": "Ответ 1", "value": 200, "used": False},
                {"question": "Вопрос 3", "answer": "Ответ 1", "value": 300, "used": False},
                {"question": "Вопрос 4", "answer": "Ответ 2", "value": 400, "used": False},
                {"question": "Вопрос 5", "answer": "Ответ 2", "value": 500, "used": False},
            ],
        }
        self.players = {}  # ключ – имя игрока, значение – набранные очки

    def add_player(self, name):
        if name and name not in self.players:
            self.players[name] = 0
            self.emit_state()

    def remove_player(self, name):
        if name in self.players:
            del self.players[name]
            self.emit_state()

    def select_question(self, topic, q_index):
        if topic in self.topics and len(self.topics[topic]) > q_index:
            q_data = self.topics[topic][q_index]
            # Если вопрос уже использован, не выбираем его
            if q_data.get("used", False):
                return
            self.state["current_topic"] = topic
            self.state["current_question"] = q_data["question"]
            self.state["current_answer"] = q_data["answer"]
            self.state["current_value"] = q_data["value"]
            self.state["show_answer"] = False
            self.state["incorrect"] = False
            self.emit_state()

    def mark_answer(self, player, correct: bool):
        if player in self.players and self.state["current_question"]:
            if correct:
                self.players[player] += self.state.get("current_value", 0)
                self.state["show_answer"] = True
                self.state["incorrect"] = False
                self.emit_state()
                # Отмечаем выбранный вопрос как использованный (не удаляем)
                topic = self.state["current_topic"]
                if topic:
                    for q_data in self.topics[topic]:
                        if q_data["question"] == self.state["current_question"]:
                            q_data["used"] = True
                            break
            else:
                # При неправильном ответе устанавливаем флаг – вопрос остаётся активным
                self.state["incorrect"] = True
                self.emit_state()

    def clear_current_question(self):
        # Сбрасываем состояние текущего вопроса (после показа ответа)
        self.state = {
            "current_topic": None,
            "current_question": None,
            "current_answer": None,
            "current_value": None,
            "show_answer": False,
            "incorrect": False,
        }
        self.emit_state()

    def is_game_over(self):
        # Игра закончена, если во всех темах все вопросы отмечены как использованные
        return all(all(q.get("used", False) for q in q_list) for q_list in self.topics.values())

    def emit_state(self):
        data = {
            "state": self.state,
            "topics": self.topics,
            "players": self.players,
            "game_over": self.is_game_over()
        }
        self.update_player_state.emit(data)

# Функция для рекурсивного очищения лэйаута
def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            clear_layout(item.layout())

# Окно ведущего
class HostWindow(QMainWindow):
    def __init__(self, controller, player_window):
        super().__init__()
        self.controller = controller
        self.player_window = player_window  # для управления слайдами в окне игроков
        self.setWindowTitle("Окно ведущего")
        self.resize(900, 700)
        self.initUI()

    def initUI(self):
        central = QWidget()
        main_layout = QVBoxLayout()

        # Отображение выбранного вопроса (ведущий видит ответ)
        self.current_question_label = QLabel("Нет выбранного вопроса")
        main_layout.addWidget(self.current_question_label)

        # Доска с темами и вопросами
        self.board_layout = QVBoxLayout()
        self.buttons = {}
        for topic, questions in self.controller.topics.items():
            h_layout = QHBoxLayout()
            topic_label = QLabel(topic)
            h_layout.addWidget(topic_label)
            for i, q in enumerate(questions):
                btn = QPushButton(f"{q['value']}")
                btn.clicked.connect(lambda checked, t=topic, idx=i: self.select_question(t, idx))
                self.buttons[(topic, i)] = btn
                h_layout.addWidget(btn)
            self.board_layout.addLayout(h_layout)
        main_layout.addLayout(self.board_layout)

        # Панель управления: выбор игрока и проверка ответа
        control_layout = QHBoxLayout()
        self.player_select = QComboBox()
        control_layout.addWidget(QLabel("Выберите игрока:"))
        control_layout.addWidget(self.player_select)
        self.btn_correct = QPushButton("Правильный")
        self.btn_incorrect = QPushButton("Неправильный")
        self.btn_correct.clicked.connect(self.mark_correct)
        self.btn_incorrect.clicked.connect(self.mark_incorrect)
        control_layout.addWidget(self.btn_correct)
        control_layout.addWidget(self.btn_incorrect)
        main_layout.addLayout(control_layout)

        # Панель для добавления и удаления игроков
        player_mgmt_layout = QHBoxLayout()
        self.player_input = QLineEdit()
        self.player_input.setPlaceholderText("Имя игрока")
        self.btn_add_player = QPushButton("Добавить игрока")
        self.btn_add_player.clicked.connect(self.add_player)
        self.btn_remove_player = QPushButton("Удалить игрока")
        self.btn_remove_player.clicked.connect(self.remove_player)
        player_mgmt_layout.addWidget(self.player_input)
        player_mgmt_layout.addWidget(self.btn_add_player)
        player_mgmt_layout.addWidget(self.btn_remove_player)
        main_layout.addLayout(player_mgmt_layout)

        # Панель переключения слайдов в окне игроков (добавлена кнопка для титров)
        slide_layout = QHBoxLayout()
        self.btn_show_welcome = QPushButton("Показать приветствие")
        self.btn_show_board = QPushButton("Показать доску")
        self.btn_show_question = QPushButton("Показать вопрос")
        self.btn_show_results = QPushButton("Показать результаты")
        self.btn_show_credits = QPushButton("Показать титры")
        self.btn_show_welcome.clicked.connect(lambda: self.player_window.set_welcome_page())
        self.btn_show_board.clicked.connect(lambda: self.player_window.set_board_page())
        self.btn_show_question.clicked.connect(lambda: self.player_window.set_question_page())
        self.btn_show_results.clicked.connect(lambda: self.player_window.set_results_page())
        self.btn_show_credits.clicked.connect(lambda: self.player_window.set_credits_page())
        slide_layout.addWidget(self.btn_show_welcome)
        slide_layout.addWidget(self.btn_show_board)
        slide_layout.addWidget(self.btn_show_question)
        slide_layout.addWidget(self.btn_show_results)
        slide_layout.addWidget(self.btn_show_credits)
        main_layout.addLayout(slide_layout)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.controller.update_player_state.connect(self.update_view)

    def select_question(self, topic, index):
        self.controller.select_question(topic, index)
        st = self.controller.state
        self.current_question_label.setText(
            f"Тема: {st['current_topic']} | Вопрос: {st['current_question']} | Ответ: {st['current_answer']}"
        )
        self.player_window.set_question_page()

    def mark_correct(self):
        player = self.player_select.currentText()
        if not player:
            QMessageBox.warning(self, "Ошибка", "Выберите игрока")
            return
        self.controller.mark_answer(player, True)
        self.player_window.set_question_page()
        # Через 3 секунды очищаем текущий вопрос и переключаем окно игроков на доску
        QTimer.singleShot(3000, self.finish_question)

    def finish_question(self):
        self.controller.clear_current_question()
        self.player_window.set_board_page()

    def mark_incorrect(self):
        player = self.player_select.currentText()
        if not player:
            QMessageBox.warning(self, "Ошибка", "Выберите игрока")
            return
        self.controller.mark_answer(player, False)
        self.player_window.set_question_page()

    def add_player(self):
        name = self.player_input.text().strip()
        if name:
            self.controller.add_player(name)
            self.player_select.addItem(name)
            self.player_input.clear()
        else:
            QMessageBox.warning(self, "Ошибка", "Введите имя игрока")

    def remove_player(self):
        player = self.player_select.currentText()
        if player:
            self.controller.remove_player(player)
            index = self.player_select.currentIndex()
            self.player_select.removeItem(index)
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите игрока для удаления")

    def update_view(self, data):
        topics = data["topics"]
        for (topic, i), btn in self.buttons.items():
            if topic in topics and len(topics[topic]) > i:
                q = topics[topic][i]
                btn.setText(f"{q['value']}")
                btn.setEnabled(not q.get("used", False))
            else:
                btn.setEnabled(False)
        st = data["state"]
        if st["current_question"]:
            self.current_question_label.setText(
                f"Тема: {st['current_topic']} | Вопрос: {st['current_question']} | Ответ: {st['current_answer']}"
            )
        else:
            self.current_question_label.setText("Нет выбранного вопроса")
        # if data.get("game_over", False):
        #     self.player_window.set_results_page()
        #     scores = data["players"]
        #     results = "\n".join(f"{p}: {s}" for p, s in scores.items())
        #     QMessageBox.information(self, "Игра окончена", f"Результаты:\n{results}")

# Окно для игроков (только для отображения)
class PlayerWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Окно игроков")
        self.resize(600, 500)
        self.initUI()
        self.controller.update_player_state.connect(self.update_view)
        # Глобальное оформление: увеличенный шрифт для всех виджетов
        self.setStyleSheet(
            "QLabel { font-size: 24px; } "
            "QPushButton { font-size: 24px; } "
            "QLineEdit { font-size: 24px; } "
            "QComboBox { font-size: 24px; }"
        )

    def initUI(self):
        self.stack = QStackedWidget()

        # Страница 0: Приветствие
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_label = QLabel("Добро пожаловать на игру 'Своя игра - 8 марта'!")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(self.welcome_label)
        self.welcome_page.setLayout(welcome_layout)
        self.stack.addWidget(self.welcome_page)

        # Страница 1: Доска с темами и вопросами (только для чтения)
        self.board_page = QWidget()
        board_layout = QVBoxLayout()
        board_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.board_container = QWidget()
        self.board_container_layout = QVBoxLayout()
        self.board_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.board_container.setLayout(self.board_container_layout)
        scroll_area.setWidget(self.board_container)
        board_layout.addWidget(scroll_area)
        self.board_page.setLayout(board_layout)
        self.stack.addWidget(self.board_page)

        # Страница 2: Страница вопроса с разделением на 3 зоны
        self.question_page = QWidget()
        q_layout = QVBoxLayout()
        q_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.topic_label = QLabel("")
        self.topic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_question_label = QLabel("")
        self.center_question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q_layout.addWidget(self.topic_label)
        q_layout.addWidget(self.center_question_label)
        q_layout.addWidget(self.feedback_label)
        self.question_page.setLayout(q_layout)
        self.stack.addWidget(self.question_page)

        # Страница 3: Итоговая страница с результатами
        self.results_page = QWidget()
        r_layout = QVBoxLayout()
        r_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_label = QLabel("")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r_layout.addWidget(self.results_label)
        self.results_page.setLayout(r_layout)
        self.stack.addWidget(self.results_page)

        # Страница 4: Титры
        self.credits_page = QWidget()
        c_layout = QVBoxLayout()
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.credits_label = QLabel("")
        self.credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(self.credits_label)
        self.credits_page.setLayout(c_layout)
        self.stack.addWidget(self.credits_page)

        self.setCentralWidget(self.stack)
        self.stack.setCurrentIndex(0)

    # Методы для переключения страниц
    def set_welcome_page(self):
        self.stack.setCurrentIndex(0)

    def set_board_page(self):
        self.populate_board()
        self.stack.setCurrentIndex(1)

    def set_question_page(self):
        self.update_question_page()
        self.stack.setCurrentIndex(2)

    def set_results_page(self):
        self.update_results_page()
        self.stack.setCurrentIndex(3)

    def set_credits_page(self):
        self.update_credits_page()
        self.stack.setCurrentIndex(4)

    def populate_board(self):
        clear_layout(self.board_container_layout)
        topics = self.controller.topics
        for topic, questions in topics.items():
            h_layout = QHBoxLayout()
            h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            topic_label = QLabel(topic)
            topic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            h_layout.addWidget(topic_label)
            for q in questions:
                btn = QPushButton(f"{q['value']}")
                btn.setEnabled(not q.get("used", False))
                h_layout.addWidget(btn)
            self.board_container_layout.addLayout(h_layout)

    def update_question_page(self):
        state = self.controller.state
        if state["current_question"]:
            self.topic_label.setText(f"{state['current_topic']}")
            self.center_question_label.setText(f"{state['current_question']}")
            if state.get("show_answer", False):
                self.feedback_label.setText(f"{state['current_answer']}")
            elif state.get("incorrect", False):
                self.feedback_label.setText("Неправильный ответ!")
            else:
                self.feedback_label.setText("")
        else:
            self.topic_label.setText("Нет выбранной темы")
            self.center_question_label.setText("Нет выбранного вопроса")
            self.feedback_label.setText("")

    def update_results_page(self):
        scores = self.controller.players
        results_text = "Результаты:\n" + "\n".join(f"{p}: {s}" for p, s in scores.items())
        self.results_label.setText(results_text)

    def update_credits_page(self):
        credits_text = "С 8 марта!\n\nСпасибо за игру!"
        self.credits_label.setText(credits_text)

    def update_view(self, data):
        if self.stack.currentIndex() == 1:
            self.populate_board()
        elif self.stack.currentIndex() == 2:
            self.update_question_page()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_red.xml')
    controller = GameController()
    # Предзаполнение списка игроков
    default_players = ["Вика", "Алина", "Интизар", "Олеся", "Оля", "Настя", "Арина", "Соня", "Милена", "Марина Юрьевна"]
    for name in default_players:
        controller.add_player(name)
    player_window = PlayerWindow(controller)
    host_window = HostWindow(controller, player_window)
    for name in default_players:
        host_window.player_select.addItem(name)
    host_window.show()
    player_window.show()
    sys.exit(app.exec())
