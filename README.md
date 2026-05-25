# Troca de Versão ECO

Aplicação desenvolvida em **Python + PyQt5** para facilitar a troca de versões do sistema ECO.

O sistema permite:

* Alterar a versão do banco (`TGERLICENCA.VERSAO`)
* Trocar rapidamente o `eco.exe`
* Organizar builds por versão

---

# Como funciona

A aplicação possui duas funções independentes:

## 1. Alterar versão

Atualiza o campo:

```sql id="uqlt71"
TGERLICENCA.VERSAO
```

A versão é obtida pelo combo selecionado na interface.

Exemplo:

```txt id="s20jbh"
1.4.680
```

Valor salvo no banco:

```txt id="g6mztf"
1468000
```

O banco é identificado automaticamente através do:

```txt id="g7rw04"
C:\ecosis\windows\eco.ini
```

---

## 2. Trocar executável

O sistema copia a build escolhida para:

```txt id="ob0cvu"
C:\ecosis\windows\eco.exe
```

Substituindo o executável atual do ECO.

---

# Estrutura de Pastas

## Pasta principal

```txt id="fjw5yl"
C:\ecosis\windows\
```

Dentro dela devem existir:

```txt id="o87s2p"
eco.exe
eco.ini
versões\
```

---

# Pasta de versões

Todas as versões devem ficar dentro de:

```txt id="0zjxlj"
C:\ecosis\windows\versões\
```

Cada versão deve possuir sua própria pasta.

Exemplo:

```txt id="g9i4mq"
C:\ecosis\windows\versões\1.4.680\
C:\ecosis\windows\versões\1.5.000\
C:\ecosis\windows\versões\1.6.000\
```

---

# Builds

Dentro de cada versão ficam os executáveis disponíveis.

Exemplo:

```txt id="1bh87t"
C:\ecosis\windows\versões\1.4.680\
│
├── 01.exe
└── 02.exe
```

Tudo que estiver dentro da pasta da versão aparecerá no campo de builds da aplicação.

---

# Exemplo completo

```txt id="trw4mq"
C:\ecosis\windows\
│
├── eco.exe
├── eco.ini
│
└── versões\
    │
    ├── 1.4.680\
    │   ├── 01.exe
    │   └── 02.exe
    │
    ├── 1.5.000\
    │   ├── eco.exe
    │   └── build_teste.exe
    │
    └── 1.6.000\
        └── eco.exe
```

---

# Instalação

## Instalar dependências

```bash id="74pbkq"
pip install PyQt5 fdb pyinstaller
```

---

# Executar projeto

```bash id="4fws6o"
python trocaversao.py
```

---

# Gerar executável

## Comando simples

```bash id="gml3of"
pyinstaller --onefile --windowed trocaversao.py
```

---

# Com ícone e nome personalizado

```bash id="p9m17v"
pyinstaller --onefile --windowed --icon=icone.ico --name="TrocaVersaoECO" trocaversao.py
```

---

# Executável gerado

```txt id="mv72bs"
dist\TrocaVersaoECO.exe
```

---

# Observações

* O sistema apenas altera a versão no banco
* Não executa updates automáticos
* Utilize o ECOUpdate após trocar versões quando necessário
* As funções de:

  * trocar versão
  * trocar executável

podem ser usadas separadamente

---

# Desenvolvedores

```txt id="f74vqk"
Mateus Garcia da Costa
Renan Augusto Mendes Carlos
```
