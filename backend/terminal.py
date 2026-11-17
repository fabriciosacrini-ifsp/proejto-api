import os
import sys

# msvcrt é a biblioteca nativa do Python no Windows para capturar teclas (como ESC) em tempo real
try:
    import msvcrt
except ImportError:
    msvcrt = None

from app import create_app
from app.services import (
    atualizar_carteira,
    atualizar_cotacao_historico,
    atualizar_investimento,
    atualizar_moeda,
    cadastrar_moeda,
    converter_valor,
    criar_carteira,
    criar_investimento,
    listar_carteira,
    listar_carteiras,
    listar_historico,
    listar_moedas_db,
    obter_resumo_moeda,
    registrar_cotacao,
    remover_carteira,
    remover_cotacao_historico,
    remover_investimento,
    remover_moeda,
)


class CanceladoPeloEsc(Exception):
    """Exceção usada internamente quando o usuário aperta a tecla ESC para voltar."""
    pass


class Cores:
    """
    Classe que centraliza as cores do Terminal (padrão ANSI) e as cores-tema de cada criptomoeda.
    """
    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    CINZA = "\033[90m"
    VERDE = "\033[92m"
    VERMELHO = "\033[91m"
    AMARELO = "\033[93m"
    CIANO = "\033[96m"

    # Cor-tema exclusiva para cada criptomoeda
    TEMAS_MOEDAS = {
        "BTC": "\033[38;5;214m",   # Laranja / Dourado Bitcoin
        "ETH": "\033[38;5;111m",   # Azul / Índigo Ethereum
        "LINK": "\033[38;5;39m",   # Azul Royal Chainlink
        "SOL": "\033[38;5;177m",   # Roxo / Lilás Solana
    }

    @classmethod
    def cor_da_moeda(cls, simbolo: str) -> str:
        """Retorna o código de cor correspondente à sigla da criptomoeda."""
        return cls.TEMAS_MOEDAS.get(simbolo.upper(), cls.CIANO)

    @classmethod
    def colorir_moeda(cls, simbolo: str, texto: str | None = None) -> str:
        """Pinta um texto com a cor-tema da criptomoeda informada."""
        cor = cls.cor_da_moeda(simbolo)
        conteudo = texto if texto is not None else simbolo.upper()
        return f"{cls.NEGRITO}{cor}{conteudo}{cls.RESET}"


class SistemaTerminalCripto:
    """
    Classe principal que gerencia a interface de Terminal (CMD) em Orientação a Objetos.
    Conta com limpeza automática de tela, cores por criptomoeda e suporte à tecla ESC.
    """

    def __init__(self):
        """Construtor: ativa cores no CMD do Windows e inicializa o app Flask + SQLite3."""
        os.system("")  # Ativa suporte a cores ANSI no CMD do Windows
        self.app = create_app()
        self.executando = True
        self.moeda_tema_atual = "BTC"

    # =================================================================
    # MÉTODOS DE TELA E LEITURA COM SUPORTE À TECLA ESC
    # =================================================================

    def limpar_tela(self):
        """Limpa o terminal para não acumular textos antigos na tela."""
        if sys.stdin.isatty():
            os.system("cls" if os.name == "nt" else "clear")

    def pausar(self):
        """Aguarda o usuário ler o resultado antes de limpar a tela novamente."""
        print(f"\n  {Cores.CINZA}Pressione [ENTER] ou [ESC] para voltar...{Cores.RESET}", end="", flush=True)
        if msvcrt and sys.stdin.isatty():
            while True:
                tecla = msvcrt.getwch()
                if tecla in ("\r", "\n", "\x1b"):
                    print()
                    return
        else:
            try:
                input()
            except (KeyboardInterrupt, EOFError):
                pass

    def _input_com_esc(self, pergunta: str) -> str:
        """
        Lê o que o usuário digita tecla por tecla no Windows.
        Se o usuário apertar ESC (\x1b), cancela imediatamente e volta à tela anterior!
        """
        print(pergunta, end="", flush=True)

        # Se não estiver em um terminal interativo do Windows, usa input() padrão
        if not (msvcrt and sys.stdin.isatty()):
            resposta = input()
            if resposta.strip().upper() == "ESC":
                raise CanceladoPeloEsc()
            return resposta

        caracteres = []
        while True:
            tecla = msvcrt.getwch()

            # Tecla ESC (\x1b): cancela na hora!
            if tecla == "\x1b":
                print(f" {Cores.AMARELO}[Cancelado com ESC]{Cores.RESET}")
                raise CanceladoPeloEsc()

            # Tecla Ctrl+C (\x03)
            if tecla == "\x03":
                print(f" {Cores.AMARELO}[Cancelado]{Cores.RESET}")
                raise CanceladoPeloEsc()

            # Tecla ENTER (\r ou \n): finaliza a digitação
            if tecla in ("\r", "\n"):
                print()
                return "".join(caracteres)

            # Tecla BACKSPACE (\x08): apaga o último caractere digitado
            if tecla == "\x08":
                if caracteres:
                    caracteres.pop()
                    print("\b \b", end="", flush=True)
                continue

            # Ignora teclas especiais (setas, F1..F12) que começam com \x00 ou \xe0
            if tecla in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue

            caracteres.append(tecla)
            print(tecla, end="", flush=True)

    def ler_texto(self, pergunta: str, obrigatorio: bool = True) -> str:
        """Lê um texto do teclado (permitindo cancelar com ESC a qualquer momento)."""
        while True:
            valor = self._input_com_esc(f"  {pergunta}").strip()
            if obrigatorio and not valor:
                print(f"  {Cores.AMARELO}[!] Este campo não pode ficar vazio (ou aperte ESC para voltar).{Cores.RESET}")
                continue
            return valor

    def ler_inteiro(self, pergunta: str) -> int:
        """Lê um número inteiro válido (ou cancela se o usuário apertar ESC)."""
        while True:
            texto = self.ler_texto(pergunta, obrigatorio=True)
            try:
                return int(texto)
            except ValueError:
                print(f"  {Cores.VERMELHO}[ERRO] Digite apenas números inteiros válidos (ou ESC para voltar)!{Cores.RESET}")

    def ler_float(self, pergunta: str) -> float:
        """Lê um valor numérico decimal aceitando vírgula ou ponto (ou cancela com ESC)."""
        while True:
            texto = self.ler_texto(pergunta, obrigatorio=True)
            try:
                return float(texto.replace(",", "."))
            except ValueError:
                print(f"  {Cores.VERMELHO}[ERRO] Digite um número válido, ex: 150 ou 150,50 (ou ESC para voltar)!{Cores.RESET}")

    def escolher_moeda(self, pergunta: str = "Sigla da criptomoeda (ex: BTC, ETH, LINK, SOL): ") -> str:
        """Exibe a tabela de criptomoedas disponíveis, lê a sigla e aplica a cor-tema."""
        moedas = listar_moedas_db()
        print("\n  ┌────────────┬──────────────────────────┐")
        print("  │ Símbolo    │ Moeda Disponível         │")
        print("  ├────────────┼──────────────────────────┤")
        for m in moedas:
            col_simb = Cores.colorir_moeda(m.simbolo, f"{m.simbolo:<10}")
            col_nome = f"{m.nome[:24]:<24}"
            print(f"  │ {col_simb} │ {col_nome} │")
        print("  └────────────┴──────────────────────────┘")

        sigla = self.ler_texto(pergunta).upper()
        self.moeda_tema_atual = sigla
        return sigla

    def formatar_brl(self, valor: float | None, mostrar_sinal: bool = False) -> str:
        """Formata um número float no padrão de moeda brasileiro (R$ 1.234,56)."""
        if valor is None:
            return "--"
        sinal = ""
        if valor < 0:
            sinal = "-"
        elif mostrar_sinal and valor > 0:
            sinal = "+"
        texto = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{sinal}R$ {texto}"

    # =================================================================
    # CABEÇALHOS COLORIDOS COM TEMA DA CRIPTOMOEDA
    # =================================================================

    def exibir_banner_topo(self, titulo_secao: str):
        """Desenha o cabeçalho no topo da tela limpa com a cor-tema da moeda atual."""
        self.limpar_tela()
        cor_tema = Cores.cor_da_moeda(self.moeda_tema_atual)
        print(f"{cor_tema}===================================================================={Cores.RESET}")
        print(f"  {Cores.NEGRITO}{cor_tema}CRIPTOMONITOR{Cores.RESET} • {Cores.NEGRITO}{titulo_secao}{Cores.RESET}")
        print(f"  {Cores.CINZA}Dica: Aperte [ESC] a qualquer momento para cancelar ou voltar{Cores.RESET}")
        print(f"{cor_tema}===================================================================={Cores.RESET}")

    # =================================================================
    # MENU PRINCIPAL
    # =================================================================

    def iniciar(self):
        """Inicia o loop principal do menu no terminal integrado ao SQLite3."""
        with self.app.app_context():
            while self.executando:
                try:
                    self.exibir_banner_topo("MENU PRINCIPAL")
                    print(f"  {Cores.colorir_moeda('BTC', '[1]')} Termômetro e Histórico de Cotações")
                    print(f"  {Cores.colorir_moeda('ETH', '[2]')} Conversor de Moedas (R$ -> Cripto)")
                    print(f"  {Cores.colorir_moeda('SOL', '[3]')} Compras da Carteira Virtual")
                    print(f"  {Cores.colorir_moeda('LINK', '[4]')} Gerenciar Carteiras de Clientes")
                    print(f"  {Cores.CIANO}{Cores.NEGRITO}[5]{Cores.RESET} Gerenciar Criptomoedas Cadastradas")
                    print(f"  {Cores.VERMELHO}{Cores.NEGRITO}[0]{Cores.RESET} Sair da Aplicação")
                    print("--------------------------------------------------------------------")

                    opcao = self.ler_texto("Escolha uma opção (0 a 5): ", obrigatorio=False)

                    if opcao == "1":
                        self.menu_cotacoes_e_termometro()
                    elif opcao == "2":
                        self.menu_conversor()
                    elif opcao == "3":
                        self.menu_investimentos()
                    elif opcao == "4":
                        self.menu_carteiras()
                    elif opcao == "5":
                        self.menu_moedas()
                    elif opcao == "0":
                        self.executando = False
                    else:
                        print(f"\n  {Cores.AMARELO}[!] Opção inválida! Escolha um número entre 0 e 5.{Cores.RESET}")
                        self.pausar()

                except CanceladoPeloEsc:
                    # Se apertar ESC no Menu Principal, pergunta se deseja sair ou apenas limpa a tela
                    self.executando = False
                except Exception as erro:
                    print(f"\n  {Cores.VERMELHO}[!] Erro inesperado tratado com segurança: {erro}{Cores.RESET}")
                    self.pausar()

            self.limpar_tela()
            print(f"\n{Cores.VERDE}====================================================================")
            print("  CriptoMonitor encerrado com segurança. Até a próxima!")
            print(f"===================================================================={Cores.RESET}\n")

    # =================================================================
    # SUBMENU 1: COTAÇÕES E TERMÔMETRO (CRUD TABELA precos_cripto)
    # =================================================================

    def menu_cotacoes_e_termometro(self):
        while True:
            try:
                self.exibir_banner_topo("1. TERMÔMETRO E HISTÓRICO DE COTAÇÕES")
                print(f"  {Cores.VERDE}[1]{Cores.RESET} Consultar cotação ao vivo na Coinbase e salvar no banco")
                print(f"  {Cores.CIANO}[2]{Cores.RESET} Ver Termômetro salvo de uma criptomoeda")
                print(f"  {Cores.CIANO}[3]{Cores.RESET} Listar histórico de cotações salvas")
                print(f"  {Cores.AMARELO}[4]{Cores.RESET} Corrigir/editar preço de uma cotação do histórico")
                print(f"  {Cores.VERMELHO}[5]{Cores.RESET} Excluir uma cotação do histórico pelo ID")
                print(f"  {Cores.CINZA}[0] Voltar ao Menu Principal (ou aperte ESC){Cores.RESET}")
                print("--------------------------------------------------------------------")

                try:
                    op = self.ler_texto("Opção: ", obrigatorio=False)
                except CanceladoPeloEsc:
                    return

                if op == "0" or not op:
                    return

                try:
                    if op == "1":
                        sigla = self.escolher_moeda()
                        print(f"\n  {Cores.CIANO}Consultando API da Coinbase para {Cores.colorir_moeda(sigla)}...{Cores.RESET}")
                        registro, termometro, erro = registrar_cotacao(sigla)
                        if erro:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Cotação salva no SQLite (ID #{registro.id})!{Cores.RESET}")
                            self.imprimir_termometro(termometro)
                        self.pausar()

                    elif op == "2":
                        sigla = self.escolher_moeda()
                        termometro, erro = obter_resumo_moeda(sigla)
                        if erro:
                            print(f"\n  {Cores.AMARELO}[AVISO] {erro}{Cores.RESET}")
                        else:
                            self.imprimir_termometro(termometro)
                        self.pausar()

                    elif op == "3":
                        sigla = self.ler_texto("Filtrar por moeda (ou ENTER para todas): ", obrigatorio=False)
                        if sigla:
                            self.moeda_tema_atual = sigla.upper()
                        registros = listar_historico(sigla if sigla else None)
                        if not registros:
                            print(f"\n  {Cores.AMARELO}Nenhuma cotação encontrada no banco.{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.NEGRITO}Histórico de Cotações ({len(registros)} registros):{Cores.RESET}")
                            print("  ┌──────┬──────────────────────┬──────────────────┬─────────────────────┐")
                            print("  │ ID   │ Moeda                │ Preço (BRL)      │ Data da Consulta    │")
                            print("  ├──────┼──────────────────────┼──────────────────┼─────────────────────┤")
                            for r in registros:
                                d = r.to_dict()
                                col_id = f"#{d['id']:<3}"
                                texto_moeda = f"{d['simbolo']} ({d['nome_moeda']})"[:20]
                                col_moeda = Cores.colorir_moeda(d["simbolo"], f"{texto_moeda:<20}")
                                col_preco = f"{self.formatar_brl(d['preco']):>16}"
                                col_data = f"{d['data_consulta']:<19}"
                                print(f"  │ {col_id} │ {col_moeda} │ {Cores.NEGRITO}{col_preco}{Cores.RESET} │ {Cores.CINZA}{col_data}{Cores.RESET} │")
                            print("  └───┴──────────────────────┴──────────────────┴─────────────────────┘".replace("└───┴", "└──────┴"))
                        self.pausar()

                    elif op == "4":
                        cotacao_id = self.ler_inteiro("ID da cotação que deseja editar: ")
                        novo_preco = self.ler_float("Novo preço em R$: ")
                        reg, erro = atualizar_cotacao_historico(cotacao_id, novo_preco)
                        if erro:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(
                                f"\n  {Cores.VERDE}[SUCESSO] Cotação #{reg.id} ({Cores.colorir_moeda(reg.simbolo)}) "
                                f"atualizada para {self.formatar_brl(reg.preco)}!{Cores.RESET}"
                            )
                        self.pausar()

                    elif op == "5":
                        cotacao_id = self.ler_inteiro("ID da cotação que deseja excluir: ")
                        ok, erro = remover_cotacao_historico(cotacao_id)
                        if not ok:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Cotação #{cotacao_id} excluída do banco de dados!{Cores.RESET}")
                        self.pausar()
                except CanceladoPeloEsc:
                    continue

            except CanceladoPeloEsc:
                return

    def imprimir_termometro(self, t: dict):
        simbolo = t["simbolo"]
        cor = Cores.cor_da_moeda(simbolo)
        cor_tendencia = (
            Cores.VERDE if t["tendencia"] == "SUBIU"
            else Cores.VERMELHO if t["tendencia"] == "CAIU"
            else Cores.AMARELO
        )
        titulo_box = f"TERMÔMETRO • {simbolo}"
        tend_txt = f"{t['tendencia']} ({t['variacao_percentual']:+.2f}%)"

        print(f"\n  {cor}┌────────────────────┬────────────────────────────────┐{Cores.RESET}")
        print(f"  {cor}│{Cores.RESET} {Cores.colorir_moeda(simbolo, f'{titulo_box:<18}')} {cor}│{Cores.RESET} {'Valores em Reais (BRL)':<30} {cor}│{Cores.RESET}")
        print(f"  {cor}├────────────────────┼────────────────────────────────┤{Cores.RESET}")
        print(f"  {cor}│{Cores.RESET} {'Preço Atual':<18} {cor}│{Cores.RESET} {Cores.NEGRITO}{self.formatar_brl(t['preco_atual']):<30}{Cores.RESET} {cor}│{Cores.RESET}")
        print(f"  {cor}│{Cores.RESET} {'Preço Anterior':<18} {cor}│{Cores.RESET} {self.formatar_brl(t['preco_anterior']):<30} {cor}│{Cores.RESET}")
        print(f"  {cor}│{Cores.RESET} {'Tendência':<18} {cor}│{Cores.RESET} {cor_tendencia}{tend_txt:<30}{Cores.RESET} {cor}│{Cores.RESET}")
        print(f"  {cor}│{Cores.RESET} {'Maior Preço (Máx)':<18} {cor}│{Cores.RESET} {Cores.VERDE}{self.formatar_brl(t['maior_preco']):<30}{Cores.RESET} {cor}│{Cores.RESET}")
        print(f"  {cor}│{Cores.RESET} {'Menor Preço (Mín)':<18} {cor}│{Cores.RESET} {Cores.VERMELHO}{self.formatar_brl(t['menor_preco']):<30}{Cores.RESET} {cor}│{Cores.RESET}")
        print(f"  {cor}│{Cores.RESET} {'Média Histórica':<18} {cor}│{Cores.RESET} {self.formatar_brl(t['media_preco']):<30} {cor}│{Cores.RESET}")
        print(f"  {cor}│{Cores.RESET} {'Total de Consultas':<18} {cor}│{Cores.RESET} {str(t['total_consultas']):<30} {cor}│{Cores.RESET}")
        print(f"  {cor}└────────────────────┴────────────────────────────────┘{Cores.RESET}")

    # =================================================================
    # SUBMENU 2: CONVERSOR DE MOEDAS
    # =================================================================

    def menu_conversor(self):
        try:
            self.exibir_banner_topo("2. CONVERSOR DE REAIS (BRL) PARA CRIPTOMOEDA")
            sigla = self.escolher_moeda()
            valor = self.ler_float("Informe o valor em Reais (R$): ")

            resultado, erro = converter_valor(sigla, valor)
            if erro:
                print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                self.pausar()
                return

            simbolo = resultado["moeda"]
            cor = Cores.cor_da_moeda(simbolo)
            titulo_conv = f"CONVERSÃO • {resultado['nome_moeda'].upper()}"[:18]
            cotacao_txt = f"1 {simbolo} = {self.formatar_brl(resultado['preco_unitario'])}"
            qtd_txt = f"{resultado['quantidade_cripto']:.8f} {simbolo}"

            print(f"\n  {cor}┌────────────────────┬────────────────────────────────┐{Cores.RESET}")
            print(f"  {cor}│{Cores.RESET} {Cores.colorir_moeda(simbolo, f'{titulo_conv:<18}')} {cor}│{Cores.RESET} {'Resultado Calculado':<30} {cor}│{Cores.RESET}")
            print(f"  {cor}├────────────────────┼────────────────────────────────┤{Cores.RESET}")
            print(f"  {cor}│{Cores.RESET} {'Valor em Reais':<18} {cor}│{Cores.RESET} {Cores.NEGRITO}{self.formatar_brl(resultado['valor_informado']):<30}{Cores.RESET} {cor}│{Cores.RESET}")
            print(f"  {cor}│{Cores.RESET} {'Cotação Atual':<18} {cor}│{Cores.RESET} {cotacao_txt:<30} {cor}│{Cores.RESET}")
            print(f"  {cor}│{Cores.RESET} {'Você Recebe':<18} {cor}│{Cores.RESET} {Cores.colorir_moeda(simbolo, f'{qtd_txt:<30}')} {cor}│{Cores.RESET}")
            if "satoshis" in resultado:
                sats_txt = f"{resultado['satoshis']:,} sats".replace(",", ".")
                print(f"  {cor}│{Cores.RESET} {'Em Satoshis':<18} {cor}│{Cores.RESET} {cor}{sats_txt:<30}{Cores.RESET} {cor}│{Cores.RESET}")
            print(f"  {cor}└────────────────────┴────────────────────────────────┘{Cores.RESET}")
            self.pausar()
        except CanceladoPeloEsc:
            return

    # =================================================================
    # SUBMENU 3: INVESTIMENTOS (CRUD TABELA investimentos)
    # =================================================================

    def menu_investimentos(self):
        while True:
            try:
                self.exibir_banner_topo("3. COMPRAS DA CARTEIRA VIRTUAL")
                print(f"  {Cores.VERDE}[1]{Cores.RESET} Simular nova compra de criptomoeda em R$")
                print(f"  {Cores.CIANO}[2]{Cores.RESET} Listar compras e calcular Lucro/Prejuízo atual")
                print(f"  {Cores.AMARELO}[3]{Cores.RESET} Editar valor investido ou carteira de uma compra")
                print(f"  {Cores.VERMELHO}[4]{Cores.RESET} Vender / Excluir uma compra pelo ID")
                print(f"  {Cores.CINZA}[0] Voltar ao Menu Principal (ou aperte ESC){Cores.RESET}")
                print("--------------------------------------------------------------------")

                try:
                    op = self.ler_texto("Opção: ", obrigatorio=False)
                except CanceladoPeloEsc:
                    return

                if op == "0" or not op:
                    return

                try:
                    if op == "1":
                        sigla = self.escolher_moeda("Qual moeda deseja comprar (BTC, ETH, LINK, SOL)? ")
                        valor = self.ler_float("Qual valor em R$ deseja investir? ")
                        carteira_txt = self.ler_texto("ID da Carteira (ENTER para Carteira Principal #1): ", obrigatorio=False)
                        carteira_id = int(carteira_txt) if carteira_txt.isdigit() else 1

                        inv, erro = criar_investimento(sigla, valor, carteira_id=carteira_id)
                        if erro:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Compra registrada no banco de dados!{Cores.RESET}")
                            self.imprimir_comprovante_compra(inv.to_dict())
                        self.pausar()

                    elif op == "2":
                        sigla = self.ler_texto("Filtrar por moeda (ou ENTER para todas): ", obrigatorio=False)
                        if sigla:
                            self.moeda_tema_atual = sigla.upper()
                        itens, resumo = listar_carteira(sigla if sigla else None, forcar_atualizacao=True)
                        if not itens:
                            print(f"\n  {Cores.AMARELO}Nenhuma compra registrada para este filtro.{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.NEGRITO}Compras Encontradas ({len(itens)}):{Cores.RESET}")
                            print("  ┌──────┬────────────────────┬────────────────────┬───────────────┬───────────────┬──────────────────────────┐")
                            print("  │ ID   │ Carteira           │ Quantidade         │ Investido     │ Valor Hoje    │ Resultado                │")
                            print("  ├──────┼────────────────────┼────────────────────┼───────────────┼───────────────┼──────────────────────────┤")
                            for item in itens:
                                cor_res = (
                                    Cores.VERDE if item["status"] == "LUCRO"
                                    else Cores.VERMELHO if item["status"] == "PREJUIZO"
                                    else Cores.AMARELO
                                )
                                col_id = f"#{item['id']:<3}"
                                txt_carteira = f"{item['nome_carteira']} (#{item['carteira_id']})"[:18]
                                col_carteira = f"{txt_carteira:<18}"

                                txt_qtd = f"{item['quantidade_cripto']:.8f} {item['simbolo']}"[:18]
                                col_qtd = Cores.colorir_moeda(item["simbolo"], f"{txt_qtd:>18}")

                                col_inv = f"{self.formatar_brl(item['valor_investido']):>13}"
                                col_hoje = f"{self.formatar_brl(item['valor_atual']):>13}"

                                txt_res = f"{self.formatar_brl(item['lucro_prejuizo'], mostrar_sinal=True)} ({item['status']})"[:24]
                                col_res = f"{cor_res}{txt_res:<24}{Cores.RESET}"

                                print(f"  │ {col_id} │ {col_carteira} │ {col_qtd} │ {col_inv} │ {col_hoje} │ {col_res} │")
                            print("  └──────┴────────────────────┴────────────────────┴───────────────┴───────────────┴──────────────────────────┘")

                            if resumo:
                                cor_tot = (
                                    Cores.VERDE if resumo["lucro_prejuizo_total"] > 0
                                    else Cores.VERMELHO if resumo["lucro_prejuizo_total"] < 0
                                    else Cores.AMARELO
                                )
                                res_geral_txt = (
                                    f"{self.formatar_brl(resumo['lucro_prejuizo_total'], mostrar_sinal=True)} "
                                    f"({resumo['variacao_total_percentual']:+.2f}%)"
                                )
                                print(f"\n  {Cores.NEGRITO}Resumo Consolidado:{Cores.RESET}")
                                print("  ┌──────────────────────┬──────────────────────┬──────────────────────────────┐")
                                print("  │ Total Investido      │ Valor Hoje           │ Resultado Geral              │")
                                print("  ├──────────────────────┼──────────────────────┼──────────────────────────────┤")
                                print(
                                    f"  │ {self.formatar_brl(resumo['total_investido']):<20} "
                                    f"│ {self.formatar_brl(resumo['total_atual']):<20} "
                                    f"│ {cor_tot}{res_geral_txt:<28}{Cores.RESET} │"
                                )
                                print("  └──────────────────────┴──────────────────────┴──────────────────────────────┘")
                        self.pausar()

                    elif op == "3":
                        inv_id = self.ler_inteiro("ID da compra que deseja atualizar: ")
                        novo_valor = self.ler_float("Novo valor investido em R$: ")
                        carteira_txt = self.ler_texto("Novo ID de Carteira (ou ENTER para manter a atual): ", obrigatorio=False)
                        nova_carteira = int(carteira_txt) if carteira_txt.isdigit() else None

                        inv, erro = atualizar_investimento(inv_id, novo_valor_investido=novo_valor, nova_carteira_id=nova_carteira)
                        if erro:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Compra atualizada com sucesso!{Cores.RESET}")
                            self.imprimir_comprovante_compra(inv.to_dict())
                        self.pausar()

                    elif op == "4":
                        inv_id = self.ler_inteiro("ID da compra que deseja vender/excluir: ")
                        ok, erro = remover_investimento(inv_id)
                        if not ok:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Compra #{inv_id} vendida/removida da carteira!{Cores.RESET}")
                        self.pausar()
                except CanceladoPeloEsc:
                    continue

            except CanceladoPeloEsc:
                return

    def imprimir_comprovante_compra(self, d: dict):
        """Exibe os dados de uma compra recém-criada ou editada em formato de tabela."""
        col_id = f"#{d['id']:<3}"
        col_carteira = f"{d['nome_carteira'][:18]:<18}"
        txt_qtd = f"{d['quantidade_cripto']:.8f} {d['simbolo']}"[:18]
        col_qtd = Cores.colorir_moeda(d["simbolo"], f"{txt_qtd:>18}")
        col_inv = f"{self.formatar_brl(d['valor_investido']):>14}"
        col_preco = f"{self.formatar_brl(d['preco_na_compra']):>16}"

        print("  ┌──────┬────────────────────┬────────────────────┬────────────────┬──────────────────┐")
        print("  │ ID   │ Carteira           │ Quantidade         │ Investido      │ Preço Unitário   │")
        print("  ├──────┼────────────────────┼────────────────────┼────────────────┼──────────────────┤")
        print(f"  │ {col_id} │ {col_carteira} │ {col_qtd} │ {Cores.NEGRITO}{col_inv}{Cores.RESET} │ {col_preco} │")
        print("  └──────┴────────────────────┴────────────────────┴────────────────┴──────────────────┘")

    # =================================================================
    # SUBMENU 4: CARTEIRAS DE INVESTIDORES (CRUD TABELA carteiras)
    # =================================================================

    def menu_carteiras(self):
        while True:
            try:
                self.exibir_banner_topo("4. GERENCIAR CARTEIRAS DE CLIENTES")
                print(f"  {Cores.VERDE}[1]{Cores.RESET} Cadastrar nova carteira")
                print(f"  {Cores.CIANO}[2]{Cores.RESET} Listar todas as carteiras")
                print(f"  {Cores.AMARELO}[3]{Cores.RESET} Editar nome, titular ou perfil de uma carteira")
                print(f"  {Cores.VERMELHO}[4]{Cores.RESET} Excluir uma carteira pelo ID")
                print(f"  {Cores.CINZA}[0] Voltar ao Menu Principal (ou aperte ESC){Cores.RESET}")
                print("--------------------------------------------------------------------")

                try:
                    op = self.ler_texto("Opção: ", obrigatorio=False)
                except CanceladoPeloEsc:
                    return

                if op == "0" or not op:
                    return

                try:
                    if op == "1":
                        nome = self.ler_texto("Nome da Carteira (ex: Reserva de Longo Prazo): ")
                        titular = self.ler_texto("Nome do Titular: ")
                        perfil = self.ler_texto("Perfil (Conservador / Moderado / Arrojado) [ENTER=Moderado]: ", obrigatorio=False)
                        c, erro = criar_carteira(nome, titular, perfil or "Moderado")
                        if erro:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Carteira #{c.id} ('{c.nome}' - {c.titular}) criada!{Cores.RESET}")
                        self.pausar()

                    elif op == "2":
                        carteiras = listar_carteiras()
                        print(f"\n  {Cores.NEGRITO}Carteiras Cadastradas ({len(carteiras)}):{Cores.RESET}")
                        print("  ┌──────┬──────────────────────────┬────────────────────┬──────────────┬─────────┐")
                        print("  │ ID   │ Nome da Carteira         │ Titular            │ Perfil       │ Compras │")
                        print("  ├──────┼──────────────────────────┼────────────────────┼──────────────┼─────────┤")
                        for c in carteiras:
                            d = c.to_dict()
                            col_id = f"#{d['id']:<3}"
                            col_nome = f"{d['nome'][:24]:<24}"
                            col_tit = f"{d['titular'][:18]:<18}"
                            col_perf = f"{d['perfil'][:12]:<12}"
                            col_comp = f"{str(d['total_compras']):^7}"
                            print(
                                f"  │ {col_id} │ {Cores.NEGRITO}{col_nome}{Cores.RESET} "
                                f"│ {col_tit} │ {Cores.CIANO}{col_perf}{Cores.RESET} │ {col_comp} │"
                            )
                        print("  └──────┴──────────────────────────┴────────────────────┴──────────────┴─────────┘")
                        self.pausar()

                    elif op == "3":
                        cid = self.ler_inteiro("ID da carteira que deseja editar: ")
                        nome = self.ler_texto("Novo nome (ou ENTER para manter): ", obrigatorio=False)
                        titular = self.ler_texto("Novo titular (ou ENTER para manter): ", obrigatorio=False)
                        perfil = self.ler_texto("Novo perfil (ou ENTER para manter): ", obrigatorio=False)

                        c, erro = atualizar_carteira(
                            cid,
                            novo_nome=nome if nome else None,
                            novo_titular=titular if titular else None,
                            novo_perfil=perfil if perfil else None,
                        )
                        if erro:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Carteira #{c.id} atualizada para '{c.nome}' ({c.titular} - {c.perfil})!{Cores.RESET}")
                        self.pausar()

                    elif op == "4":
                        cid = self.ler_inteiro("ID da carteira que deseja excluir: ")
                        ok, erro = remover_carteira(cid)
                        if not ok:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Carteira #{cid} removida com sucesso!{Cores.RESET}")
                        self.pausar()
                except CanceladoPeloEsc:
                    continue

            except CanceladoPeloEsc:
                return

    # =================================================================
    # SUBMENU 5: MOEDAS CADASTRADAS (CRUD TABELA moedas)
    # =================================================================

    def menu_moedas(self):
        while True:
            try:
                self.exibir_banner_topo("5. GERENCIAR CRIPTOMOEDAS CADASTRADAS")
                print(f"  {Cores.VERDE}[1]{Cores.RESET} Cadastrar nova criptomoeda (ex: ADA, DOGE, XRP)")
                print(f"  {Cores.CIANO}[2]{Cores.RESET} Listar todas as criptomoedas cadastradas")
                print(f"  {Cores.AMARELO}[3]{Cores.RESET} Editar o nome de uma criptomoeda")
                print(f"  {Cores.VERMELHO}[4]{Cores.RESET} Remover uma criptomoeda pelo ID")
                print(f"  {Cores.CINZA}[0] Voltar ao Menu Principal (ou aperte ESC){Cores.RESET}")
                print("--------------------------------------------------------------------")

                try:
                    op = self.ler_texto("Opção: ", obrigatorio=False)
                except CanceladoPeloEsc:
                    return

                if op == "0" or not op:
                    return

                try:
                    if op == "1":
                        simbolo = self.ler_texto("Sigla da criptomoeda (ex: ADA, DOGE, XRP): ")
                        nome = self.ler_texto("Nome completo da moeda (ex: Cardano, Dogecoin): ")
                        print(f"\n  {Cores.CIANO}Validando par em BRL na Coinbase...{Cores.RESET}")
                        m, erro = cadastrar_moeda(simbolo, nome)
                        if erro:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            self.moeda_tema_atual = m.simbolo
                            print(f"\n  {Cores.VERDE}[SUCESSO] Moeda #{m.id} ({Cores.colorir_moeda(m.simbolo, f'{m.simbolo} - {m.nome}')}) cadastrada!{Cores.RESET}")
                        self.pausar()

                    elif op == "2":
                        moedas = listar_moedas_db()
                        print(f"\n  {Cores.NEGRITO}Criptomoedas Cadastradas ({len(moedas)}):{Cores.RESET}")
                        print("  ┌──────┬────────────┬──────────────────────────────┐")
                        print("  │ ID   │ Símbolo    │ Nome da Criptomoeda          │")
                        print("  ├──────┼────────────┼──────────────────────────────┤")
                        for m in moedas:
                            col_id = f"#{m.id:<3}"
                            col_simb = Cores.colorir_moeda(m.simbolo, f"{m.simbolo:<10}")
                            col_nome = f"{m.nome[:28]:<28}"
                            print(f"  │ {col_id} │ {col_simb} │ {col_nome} │")
                        print("  └──────┴────────────┴──────────────────────────────┘")
                        self.pausar()

                    elif op == "3":
                        mid = self.ler_inteiro("ID da moeda que deseja editar: ")
                        novo_nome = self.ler_texto("Novo nome para a moeda: ")
                        m, erro = atualizar_moeda(mid, novo_nome)
                        if erro:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Moeda #{m.id} ({Cores.colorir_moeda(m.simbolo)}) atualizada para '{m.nome}'!{Cores.RESET}")
                        self.pausar()

                    elif op == "4":
                        mid = self.ler_inteiro("ID da moeda que deseja remover: ")
                        ok, erro = remover_moeda(mid)
                        if not ok:
                            print(f"\n  {Cores.VERMELHO}[ERRO] {erro}{Cores.RESET}")
                        else:
                            print(f"\n  {Cores.VERDE}[SUCESSO] Moeda #{mid} removida do banco de dados!{Cores.RESET}")
                        self.pausar()
                except CanceladoPeloEsc:
                    continue

            except CanceladoPeloEsc:
                return


if __name__ == "__main__":
    sistema = SistemaTerminalCripto()
    sistema.iniciar()
