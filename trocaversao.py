import os
import shutil
import logging
import configparser
from pathlib import Path

import fdb

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
)

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# =========================================================
# CONFIGURAÇÕES
# =========================================================

BASE_DIR = Path(r"C:\ecosis\windows")

PASTA_VERSOES = BASE_DIR / "versões"
ECO_INI = BASE_DIR / "eco.ini"

EXECUTAVEL_DESTINO = BASE_DIR / "eco.exe"

USUARIO_FB = "SYSDBA"
SENHA_FB = "masterkey"

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================


def exibir_erro(parent: QWidget, mensagem: str) -> None:
    """
    Exibe uma mensagem de erro padrão.
    """

    QMessageBox.critical(
        parent,
        "Erro",
        mensagem
    )


def exibir_sucesso(parent: QWidget, mensagem: str) -> None:
    """
    Exibe uma mensagem de sucesso padrão.
    """

    QMessageBox.information(
        parent,
        "Sucesso",
        mensagem
    )


# =========================================================
# BANCO DE DADOS
# =========================================================

def ler_configuracao_banco() -> tuple[str, str]:
    """
    Lê o eco.ini e retorna:

    Returns
    -------
    tuple[str, str]
        host, caminho_banco
    """

    if not ECO_INI.exists():
        raise FileNotFoundError(
            "Arquivo eco.ini não encontrado."
        )

    config = configparser.ConfigParser()
    config.read(ECO_INI, encoding="latin-1")

    for secao in config.sections():

        if config.has_option(secao, "DADOS"):

            valor_dados = config.get(secao, "DADOS")

            try:
                host, banco = valor_dados.split(":", 1)

            except ValueError:
                raise Exception(
                    "Formato inválido no campo DADOS."
                )

            return host, banco

    raise Exception(
        "Campo DADOS não encontrado no eco.ini."
    )


def conectar_banco() -> fdb.Connection:
    """
    Cria conexão com banco Firebird.
    """

    host, banco = ler_configuracao_banco()

    logging.info(
        "Conectando ao banco %s em %s",
        banco,
        host
    )

    return fdb.connect(
        host=host,
        database=banco,
        user=USUARIO_FB,
        password=SENHA_FB,
        charset="WIN1252"
    )


# =========================================================
# REGRAS DE NEGÓCIO
# =========================================================

def gerar_versao_tgerlicenca(versao: str) -> int:
    """
    Converte versão para padrão utilizado na tabela
    TGERLICENCA.

    Exemplo
    --------
    680 -> 680000
    """

    versao_limpa = (
        versao
        .replace(".", "")
        .replace(",", "")
    )

    return int(f"{versao_limpa}000")


# ============================================
# ATUALIZAR A VERSÃO DO BANCO
# ============================================

def atualizar_versao_banco(versao: str) -> int:
    """
    Atualiza campo VERSAO da tabela TGERLICENCA.
    """

    valor_versao = gerar_versao_tgerlicenca(
        versao
    )

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute(
            """
            UPDATE TGERLICENCA
            SET VERSAO = ?
            """,
            (valor_versao,)
        )

        conexao.commit()

        logging.info(
            "Versão alterada para %s",
            valor_versao
        )

        return valor_versao

    finally:
        conexao.close()


def copiar_executavel(
    versao: str,
    build: str
) -> None:
    """
    Copia executável selecionado para pasta principal.
    """

    origem = PASTA_VERSOES / versao / build

    if not origem.exists():

        raise FileNotFoundError(
            f"Build não encontrada:\n{origem}"
        )

    shutil.copy2(
        origem,
        EXECUTAVEL_DESTINO
    )

    logging.info(
        "Executável %s copiado com sucesso.",
        build
    )


# =========================================================
# JANELA DE INFORMAÇÕES
# =========================================================

from PyQt5.QtWidgets import QDialog, QTextEdit


class JanelaInformacoes(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("INFORMAÇÕES ADICIONAIS")
        self.setFixedSize(430, 320)

        self.setStyleSheet("""
            QDialog {
                background-color: #181a1f;
                color: white;
                font-size: 20px;
                font-family: Segoe UI;
            }

            QTextEdit {
                background-color: #181a1f;
                border: none;
                color: white;
                padding: 13px;
                selection-background-color: #2d7dd2;
            }
        """)

        texto = """

    - A base alterada será aquela definida no ECO.ini

    - A versão será alterada apenas na tabela TGERLICENCA,
        para garantir a atualização correta, utilize o ECOUpdate.

    - Crie uma pasta separada para cada versão do ECO no caminho:
        C:\\ecosis\\windows\\versões\\

    - Dentro de cada pasta, armazene os respectivos executáveis.
        Exemplo: C:\\ecosis\\windows\\versões\\1.4.680\\11.exe

    - As duas funções podem ser utilizadas independentemente.
    
    - Para mais informações e para ter acesso ao código fonte, acesse 
        esse repositório

https://github.com/MateusGarciaaa/TrocaVersaoEcoCentauro.git

                Uso interno Ecocentauro Sistemas. Feito por:
                        Mateus Garcia da Costa  
                        Renan Augusto Mendes Carlos.
"""

        layout = QVBoxLayout()

        area_texto = QTextEdit()
        area_texto.setReadOnly(True)
        area_texto.setText(texto)

        layout.addWidget(area_texto)

        self.setLayout(layout)


# =========================================================
# INTERFACE
# =========================================================

class TelaPrincipal(QWidget):

    """
    Interface principal da aplicação.
    """

    def __init__(self):
        super().__init__()

        self.configurar_janela()
        self.criar_componentes()
        self.criar_layout()
        self.carregar_versoes()

    # =====================================================
    # CONFIGURAÇÃO
    # =====================================================

    def configurar_janela(self) -> None:

        self.setWindowTitle(
            "Troca de versão ECO"
        )

        self.setFixedSize(270, 150)

        #270 150

        self.setStyleSheet("""
            QWidget {
                background-color: #181a1f;     
                color: #f1f1f1;
                font-size: 13px;
                font-family: Segoe UI;
            }

                           

            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #d6d6d6;              
                margin-bottom: 3px;
            }

            QComboBox {
                background-color: #23272e;
                border: 1px solid #3b4048;
                border-radius: 8px;
                padding: 4px;
                color: white;
            }

            QComboBox:hover {
                border: 1px solid #4ea1ff;
            }

            QComboBox::drop-down {
                border: none;
                width: 25px;
            }

            QComboBox::down-arrow {
                image: none;
            }

            QPushButton {
                background-color: #2d7dd2;
                border: none;
                border-radius: 10px;
                padding: 5px;
                font-size: 13px;
                font-weight: bold;
                color: white;
            }

            QPushButton:hover {
                background-color: #3693ff;
            }

            QPushButton:pressed {
                background-color: #1f5fa8;
            }

            QMessageBox {
                background-color: #23272e;
                msg.setTextFormat(Qt.RichText)
                msg.setText(texto)
                msg.setOpenExternalLinks(True)    
            }

            QToolTip {
                background-color: #2d2f36;
                color: white;
                border: 1px solid #4ea1ff;
                padding: 5px;
            }
        """)

    # =====================================================
    # COMPONENTES
    # =====================================================

    def criar_componentes(self) -> None:

        self.label_versao = QLabel(
            "Selecione a versão"
        )



        self.combo_versao = QComboBox()
        self.combo_versao.currentTextChanged.connect(
            self.carregar_builds
        )

        self.label_build = QLabel(
            "Selecione a build"
        )

        self.combo_build = QComboBox()

        self.botao_versao = QPushButton(
            "Alterar Versão"
        )

        self.botao_versao.clicked.connect(
            self.alterar_versao
        )

        self.botao_executavel = QPushButton(
            "Trocar Executável"
        )

        self.botao_executavel.clicked.connect(
            self.trocar_executavel
        )

        self.botao_info = QPushButton("?")

        self.botao_info.setFixedSize(28, 28)

        self.botao_info.clicked.connect(
            self.abrir_informacoes
        )

        self.combo_versao.setFixedHeight(28)
        self.combo_build.setFixedHeight(28)

        self.botao_versao.setFixedHeight(28)
        self.botao_executavel.setFixedHeight(28)

        self.botao_info.setFixedSize(26, 26)

    # =====================================================
    # LAYOUT
    # =====================================================

    def criar_layout(self) -> None:

        layout_principal = QVBoxLayout()

        layout_principal.setSpacing(6)

        layout_principal.setContentsMargins(
            12,
            6,
            12,
            12
        )

        # ====================================
        # LABEL + BOTÃO INFO
        # ====================================

        linha_label_versao = QHBoxLayout()

        linha_label_versao.addWidget(
            self.label_versao
        )

        linha_label_versao.addStretch()

        linha_label_versao.addWidget(
            self.botao_info
        )

        # ====================================
        # LINHA VERSÃO
        # ====================================

        linha_versao = QHBoxLayout()

        linha_versao.addWidget(
            self.combo_versao
        )

        linha_versao.addWidget(
            self.botao_versao
        )

        # ====================================
        # LINHA BUILD
        # ====================================

        linha_build = QHBoxLayout()

        linha_build.addWidget(
            self.combo_build
        )

        linha_build.addWidget(
            self.botao_executavel
        )

        # ====================================

        layout_principal.addLayout(
            linha_label_versao
        )

        layout_principal.addLayout(
            linha_versao
        )

        layout_principal.addWidget(
            self.label_build
        )

        layout_principal.addLayout(
            linha_build
        )

        self.setLayout(layout_principal)

    # =====================================================
    # VERSÕES
    # =====================================================

    def carregar_versoes(self) -> None:

        self.combo_versao.clear()

        if not PASTA_VERSOES.exists():
            return

        versoes = sorted([
            pasta.name
            for pasta in PASTA_VERSOES.iterdir()
            if pasta.is_dir()
        ])

        self.combo_versao.addItems(
            versoes
        )

    def carregar_builds(self) -> None:
        self.combo_build.clear()

        versao = self.combo_versao.currentText()

        if not versao:
            return

        pasta_versao = PASTA_VERSOES / versao

        if not pasta_versao.exists():
            return

        builds = sorted([
            arquivo.name
            for arquivo in pasta_versao.iterdir()
            if arquivo.is_file()
        ])

        self.combo_build.addItems(builds)

    # =====================================================
    # AÇÕES
    # =====================================================

    def alterar_versao(self) -> None:
        try:
            versao = self.combo_versao.currentText()
            if not versao:
                raise Exception(
                    "Selecione uma versão."
                )
            valor = atualizar_versao_banco(
                versao
            )
            exibir_sucesso(
                self,
                f"VERSAO alterada para:\n{valor}"
            )

        except Exception as erro:
            logging.exception(
                "Erro ao alterar versão."
            )
            exibir_erro(
                self,
                str(erro)
            )

    def trocar_executavel(self) -> None:
        try:
            versao = self.combo_versao.currentText()
            build = self.combo_build.currentText()

            if not versao or not build:
                raise Exception(
                    "Selecione uma build."
                )

            copiar_executavel(
                versao,
                build
            )
            exibir_sucesso(
                self,
                f"Executável trocado:\n{build}"
            )

        except Exception as erro:
            logging.exception(
                "Erro ao trocar executável."
            )
            exibir_erro(
                self,
                str(erro)
            )

    def abrir_informacoes(self) -> None:
        janela = JanelaInformacoes()
        janela.exec_()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    app = QApplication([])

    janela = TelaPrincipal()
    janela.show()

    app.exec_()