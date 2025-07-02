Utils = { }


function Utils.getCardData(card)
    local _card = { }

    if(card.ability.set == "Default") then 
        _card.type = "Card"
        _card.id        = card.base.id
        _card.suit      = card.base.suit
        _card.effect    = card.ability.effect
        _card.cost      = card.cost
        _card.sell_cost = card.sell_cost
        if(card.seal == nil) then 
            _card.seal = "None"
        else
            _card.seal = card.seal
        end
    elseif(card.ability.set == "Joker") then
        _card.type = card.ability.set
        _card.ability   = card.ability.name
        if(card.edition == nil) then _card.edition = "None"
        else _card.edition = card.edition end
        _card.cost      = card.cost
        _card.sell_cost = card.sell_cost
    else
        _card.type = card.ability.set
        _card.ability = card.ability.name
        _card.cost      = card.cost
        _card.sell_cost = card.sell_cost
    end
   

    return _card
end

function Utils.getDeckData()
    local _deck = { }
    local i = 1
    if G and G.playing_cards then
        for k, card in pairs(G.playing_cards) do
            local _card = Utils.getCardData(card)
            _deck[i] = _card
            i = i+1
        end
    end
    return _deck
end

function Utils.getHandData()
    local _hand = { }

    if G and G.hand and G.hand.cards then
        for i = 1, #G.hand.cards do
            local _card = Utils.getCardData(G.hand.cards[i])
            _hand[i] = _card
        end
    end

    return _hand
end

function Utils.getJokersData()
    local _jokers = { }

    if G and G.jokers and G.jokers.cards then
        for i = 1, #G.jokers.cards do
            local _card = Utils.getCardData(G.jokers.cards[i])
            _jokers[i] = _card
        end
    end

    return _jokers
end

function Utils.getConsumablesData()
    local _consumables = { }

    if G and G.consumeables and G.consumeables.cards then
        for i = 1, #G.consumeables.cards do
            local _card = Utils.getCardData(G.consumeables.cards[i])
            _consumables[i] = _card
        end
    end

    return _consumables
end

function Utils.getBlindData()
    local _blinds = { }

    if G and G.GAME then
        _blinds.ondeck = G.GAME.blind_on_deck
    end

    return _blinds
end

function Utils.getBlindData()
    local _blinds = { }

    if G and G.GAME then
        _blinds.ondeck = G.GAME.blind_on_deck
    end

    return _blinds
end

function Utils.getAnteData()
    local _ante = { }
    _ante.blinds = Utils.getBlindData()

    return _ante
end

function Utils.getBackData()
    local _back = { }
    --###########################################
    return _back
end


function Utils.getShopData()
    local _shop = { }
    if not G or not G.shop then return _shop end
    
    _shop.reroll_cost = G.GAME.current_round.reroll_cost
    _shop.cards = { }
    _shop.boosters = { }
    _shop.vouchers = { }

    for i = 1, #G.shop_jokers.cards do
        _shop.cards[i] = Utils.getCardData(G.shop_jokers.cards[i])
    end

    for i = 1, #G.shop_booster.cards do
        _shop.boosters[i] = Utils.getCardData(G.shop_booster.cards[i])
    end

    for i = 1, #G.shop_vouchers.cards do
        _shop.vouchers[i] = Utils.getCardData(G.shop_vouchers.cards[i])
    end

    return _shop
end

function Utils.getHandScoreData()
    local _handscores = { }
    --###########################################

    return _handscores
end

function Utils.getHandsData()
    local _hands = { }

    if G and G.GAME and G.GAME.hands then
        for k, v in pairs(G.GAME.hands) do
            data = {}
            data.level = v.level
            data.played_this_round = v.played_this_round
            _hands[k] = data
        end 
    end
    return _hands
end
function Utils.getTagsData()
    local _tags = {}
    if G and G.GAME and G.GAME.tags then
        for i=1, #G.GAME.tags do
            _tags[i] = G.GAME.tags[i].name
        end
    end
    return _tags
end

function Utils.getRoundData()
    local _current_round = { }

    if G and G.GAME and G.GAME.current_round then
        _current_round.discards_left = G.GAME.current_round.discards_left
        _current_round.hands_left = G.GAME.current_round.hands_left
    end

    return _current_round
end

function Utils.getVouchers()
    local _vouchers = {}
    
    if G and G.GAME and G.GAME.used_vouchers then
        i = 1
        for k, v in pairs(G.GAME.used_vouchers) do
            _vouchers[i] = k
            i = i+1
        end
    end
    return _vouchers
end
function Utils.getGameData()
    local _game = { }

    if G.GAME then
        _game.hands_played = G.GAME.hands_played
        _game.Skips = G.GAME.Skips
        _game.round = G.GAME.round
        _game.dollars = G.GAME.dollars
        _game.max_jokers = G.GAME.max_jokers
        _game.bankrupt_at = G.GAME.bankrupt_at
        _game.chips = G.GAME.chips
        
    end

    return _game
end

function Utils.getGamestate()
    local _gamestate = {}

    _gamestate.state = G.STATE
    _gamestate.waiting_for = G.waitingFor
    _gamestate.game = Utils.getGameData()
    _gamestate.hand = Utils.getHandData()
    _gamestate.jokers = Utils.getJokersData()
    _gamestate.consumables = Utils.getConsumablesData()
    _gamestate.shop = Utils.getShopData()
    _gamestate.current_round = Utils.getRoundData()
    _gamestate.used_vouchers = Utils.getVouchers()
    _gamestate.handsData = Utils.getHandsData()
    _gamestate.current_hand = G.GAME.current_round.current_hand
    return _gamestate
end

function Utils.getRoundData()
    local _round = { }

    if G and G.GAME and G.GAME.current_round then
        _round.discards_left = G.GAME.current_round.discards_left
        _round.hands_left = G.GAME.current_round.hands_left
        _round.blind_on_deck = G.GAME.blind_on_deck
        _round.reroll_cost = G.GAME.current_round.reroll_cost
    end

    return _round
end

function Utils.parseaction(data)
    -- Protocol is ACTION|arg1|arg2
    action = data:match("^([%a%u_]*)")
    params = data:match("|(.*)")

    if action then
        local _action = Bot.ACTIONS[action]

        if not _action then
            return nil
        end

        local _actiontable = { }
        _actiontable[1] = _action

        if params then
            local _i = 2
            for _arg in params:gmatch("[%w%s,]+") do
                local _splitstring = { }
                local _j = 1
                for _str in _arg:gmatch('([^,]+)') do
                    _splitstring[_j] = tonumber(_str) or _str
                    _j = _j + 1
                end
                _actiontable[_i] = _splitstring
                _i = _i + 1
            end
        end

        return _actiontable
    end
end

Utils.ERROR = {
    NOERROR = 1,
    NUMPARAMS = 2,
    MSGFORMAT = 3,
    INVALIDACTION = 4,
}

function Utils.validateAction(action)
    if action and #action > 1 and #action > Bot.ACTIONPARAMS[action[1]].num_args then
        return Utils.ERROR.NUMPARAMS
    elseif not action then
        return Utils.ERROR.MSGFORMAT
    else
        if not Bot.ACTIONPARAMS[action[1]].isvalid(action) then
            return Utils.ERROR.INVALIDACTION
        end
    end

    return Utils.ERROR.NOERROR
end

function Utils.isTableUnique(table)
    if table == nil then return true end

    local _seen = { }
    for i = 1, #table do
        if _seen[table[i]] then return false end
        _seen[table[i]] = table[i]
    end

    return true
end

function Utils.isTableInRange(table, min, max)
    if table == nil then return true end

    for i = 1, #table do
        if table[i] < min or table[i] > max then return false end
    end
    return true
end

return Utils