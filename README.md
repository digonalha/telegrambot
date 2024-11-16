### esse projeto saiu um pouco do controle e ficou meio disfuncional. caso queira mandar prs, ficarei feliz em revisa-los e aprovar. um dia volto a mexer nele.
### material para estudo, bot Taxador está desativado por tempo indefinido.
### metodo de consumo da api do correios não funciona mais, está desabilitado no momento.


# telegrambot

Essa aplicação tem três propósitos: gerenciar grupos, monitorar promoções e rastrear objetos na api do Correios no Telegram. Preferi não utilizar nenhuma biblioteca já conhecido da API do telegram e criar a minha própria por motivos de estudo. Também utilizo BeautifulSoup para fazer webscraper na hora de buscar promoções. Você pode testar o bot pelo link abaixo:

https://t.me/taxadorbot

# Como executar a aplicação:
Crie um arquivo .env no modelo do .env.example (se não estiver criado e preenchido, a aplicação não irá iniciar)

Tenha o docker e docker-compose instalados na máquina. Entrar na pasta raiz do repositório e executar o comando: 

**docker-compose up --build -d**

E pronto! Após a execução do comando, será instalado o banco de dados postgres e a aplicação telegrambot.

# No momento o bot atende os seguintes comandos:

## Dentro de grupos:
```
/help: lista os comandos disponíveis no grupo
/mod <username>: promove o usuário ao cargo de moderador *
/unmod <username>: rebaixa o usuário do cargo de moderador *
/mute <username> <tempo em segundos>: adiciona o usuário na lista de silenciados pelo tempo especificado **
/unmute <username>: remove o usuário da lista de silenciados **
/cmd: lista os comandos customizados disponíveis no grupo
/addcmd <comando> | <resposta>(obrigatório quando não há midia) | <descrição>: adiciona um novo comando (para mídias, enviar o comando na legenda) **
/delcmd <comando>: remove um comando customizado *

* necessário ser um administrador (do bot)
** necessário ser um administrador ou moderador
```

------

Para o bot identificar o usuário nos comandos pelo username, ele precisa indexar esse usuario no banco de dados.

------

Os comandos do tipo texto podem ser cadastrados para retornar números ou palavras aleatórias. Para isso você deve utilizar na reposta os patterns abaixo:

**$random_number\[x,y\] (intervalo entre 2 números)**

**$random_word\[word1,word2,...,word10\] (máx. 10 palavras)**

## No chat privado

Com o tempo, adicionei uma funcionalidade para que ele monitore promoçoes e notifique os usuários. Para utilizar essa funcionalidade veja os comandos abaixo:
```
/help: lista os comandos disponíveis no chat privado
/promo <palavra-chave>(opcional): lista as promoções cadastradas pelo usuário. Quando o comando é enviado c/ palavra-chave, lista as promoções das ultimas 24 horas relacionadas a palavra-chave.
/addpromo <palavra-chave> | <valor-máx>(opcional): adiciona ou atualiza uma palavra-chave no monitor de promoções do usuário (caso não seja passado o valor máximo, todas as promoções são notificadas)
/delpromo <palavra-chave>: remove a palavra-chave da lista de monitoramento de promoções
/clearpromo: remove todas as palavras-chave da lista de monitoramento de promoções
/rastreio <código>(opcional)- lista os códigos de rastreio dos correios monitorados pelo usuário. Quando o comando é enviado c/ código, lista os eventos de rastreio relacionados ao código enviado.
/addrastreio código-rastreio | nome(opcional) - adiciona um código de rastreio no serviço de rastreio dos correios
/delrastreio código-rastreio - remove um código de rastreio do serviço de rastreio dos correios
```

Qualquer duvida, report de bugs, sugestões de melhorias pode entrar em contato por issue.
