# telegrambot

Essa aplicação tem dois propósitos: Gerenciar Grupos e Monitorar Promoções no Telegram. Preferi não utilizar nenhuma biblioteca já conhecido da API do telegram e criar a minha própria por motivos de estudo. Também utilizo BeautifulSoup para fazer webscraper na hora de buscar promoções. Você pode testar o bot pelo link abaixo:

https://t.me/taxadorbot

# Como executar a aplicação:
Crie um arquivo .env no modelo do .env.example (se não estiver criado e preenchido, a aplicação não irá iniciar)

Tenha o docker e docker-compose instalados na máquina. Entrar na pasta raiz do repositório e executar o comando: 
docker-compose up --build -d

E pronto! Após a execução do comando, será instalado o banco de dados postgres e a aplicação telegrambot.

No momento o bot atende os seguintes comandos:

## Dentro de grupos:
```
/help: lista os comandos disponíveis no grupo
/mod <username>: promove o usuário ao cargo de moderador *
/unmod <username>: rebaixa o usuário do cargo de moderador *
/mute <username> <tempo em segundos>: adiciona o usuário na lista de silenciados pelo tempo especificado **
/unmute <username>: remove o usuário da lista de silenciados **
/cmd: lista os comandos customizados disponíveis no grupo
/addcmd <comando> | <resposta> | <descrição>: adiciona um novo comando (para mídias, enviar o comando na legenda) **
/delcmd <comando>: remove um comando customizado *

* necessário ser um administrador (do bot)
** necessário ser um administrador ou moderador
```

Para o bot identificar o usuário pelo username, ele precisa indexar esse usuario no banco. Pra fazer isso, sempre que vai verificar as novas mensagens do canal, ele valida se o usuario que enviou a mensagem já está na lista de usuários conhecidos, e quando o usuário nao é encontrado ele adiciona ao banco e insere na lista de usuários conhecidos.

## No chat privado

Com o tempo, adicionei uma funcionalidade para que ele monitore promoçoes e notifique os usuários. Para utilizar essa funcionalidade veja os comandos abaixo:
```
/help: lista os comandos disponíveis no chat privado
/promo: lista as promoções cadastradas pelo usuário
/lastpromo <palavra-chave>: lista as promoções das ultimas 24 horas relacionadas a palavra-chave.
/addpromo <palavra-chave> | <opcional:valor-máx>: adiciona ou atualiza uma palavra-chave no monitor de promoções do usuário (caso não seja passado o valor máximo, todas as promoções são notificadas)
/delpromo <palavra-chave>: remove a palavra-chave da lista de monitoramento de promoções
/clearpromo: remove todas as palavras-chave da lista de monitoramento de promoções
```

Qualquer duvida, report de bugs, sugestões de melhorias pode entrar em contato comigo por issue. :)
