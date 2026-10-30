# --
# -- This is GarboChess engine by Gary Linscott (The author)
# -- http://forwardcoding.com
# --
# -------------------------------------------------------------------
# --
# -- ported to python from javascript by Chessforeva
# -- Just could not resist, this is absolutely brilliant code for
# -- interpreted chess - the optimal AI for scripting :)
# -- Very needed. Just could not find better.
# --

import time

if(True):

    global g_timeout, g_maxfinCnt, g_startTime, g_finCnt, g_foundmove, colorBlack, colorWhite
    global pieceEmpty, piecePawn, pieceKnight, pieceBishop, pieceRook, pieceQueen, pieceKing
    global g_vectorDelta, g_vectdelta, g_bishopDeltas, g_knightDeltas, g_rookDeltas, g_queenDeltas
    global g_castleRightsMask, moveflagEPC, moveflagCastleKing, moveflagCastleQueen, moveflagPromotion
    global moveflagPromoteKnight, moveflagPromoteQueen, moveflagPromoteBishop
    global g_board, g_toMove, g_castleRights, g_enPassentSquare, g_seeValues
    global g_baseEval, g_hashKeyLow, g_hashKeyHigh, g_inCheck
    global g_moveCount, g_moveUndoStack, g_move50, g_repMoveStack, g_hashSize, g_hashMask
    global g_hashTable, g_killers, historyTable, g_zobristLow, g_zobristHigh, g_zobristBlackLow
    global g_zobristBlackHigh, g_mobUnit, hashflagAlpha, hashflagBeta, hashflagExact
    global g_nodeCount, g_qNodeCount,  g_searchValid
    global minEval, maxEval, minMateBuffer, maxMateBuffer, materialTable
    global pawnAdj, knightAdj, bishopAdj, rookAdj, kingAdj, emptyAdj, pieceSquareAdj
    global flipTable, g_pieceIndex, g_pieceList, g_pieceCount, PieceCharList

   
    g_timeout = 30             #-- can set maximum seconds for analysing
    g_maxfinCnt = 100000       #-- can set limit of moves to analyse
    
    g_startTime = 0
    g_finCnt = 0
    
    g_foundmove = 0
    
    # --
    # -- Board code
    # --
    
    # -- This somewhat funky scheme means that a piece is indexed by it's lower 4 bits when accessing in arrays.  The fifth bit (black bit)
    # -- is used to allow quick edge testing on the board.
    
    colorBlack = 0x10
    colorWhite = 0x08
    
    pieceEmpty = 0x00
    piecePawn = 0x01
    pieceKnight = 0x02
    pieceBishop = 0x03
    pieceRook = 0x04
    pieceQueen = 0x05
    pieceKing = 0x06
                           # PieceMask
    g_vectorDelta  = [[0 for x in range(256)] for x in range(256)]     #-- new Array(256x256)
    g_vectdelta = [0 for x in range(256)]                              #-- new Array(256)
   
    g_bishopDeltas = [-15, -17, 15, 17]
    g_knightDeltas = [31, 33, 14, -14, -31, -33, 18, -18]
    g_rookDeltas = [-1, 1, -16, 16]
    g_queenDeltas = [-1, 1, -15, 15, -17, 17, -16, 16]
    
    g_seeValues = [0, 1, 3, 3, 5, 9, 900, 0, 0, 1, 3, 3, 5, 9, 900, 0]
    
    g_castleRightsMask = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 7,15,15,15, 3,15,15,11, 0, 0, 0, 0,
    0, 0, 0, 0,15,15,15,15,15,15,15,15, 0, 0, 0, 0,
    0, 0, 0, 0,15,15,15,15,15,15,15,15, 0, 0, 0, 0,
    0, 0, 0, 0,15,15,15,15,15,15,15,15, 0, 0, 0, 0,
    0, 0, 0, 0,15,15,15,15,15,15,15,15, 0, 0, 0, 0,
    0, 0, 0, 0,15,15,15,15,15,15,15,15, 0, 0, 0, 0,
    0, 0, 0, 0,15,15,15,15,15,15,15,15, 0, 0, 0, 0,
    0, 0, 0, 0,13,15,15,15,12,15,15,14, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
    
    moveflagEPC = (0x2 << 16)
    moveflagCastleKing = (0x4 << 16)
    moveflagCastleQueen = (0x8 << 16)
    moveflagPromotion = (0x10 << 16)
    moveflagPromoteKnight = (0x20 << 16)
    moveflagPromoteQueen = (0x40 << 16)
    moveflagPromoteBishop = (0x80 << 16)
    
    # -- Position variables
    
    g_board = [0x80 for x in range(256)]    #-- new Array(256); -- Sentinel 0x80, pieces are in low 4 bits, 0x8 for color, 0x7 bits for piece type
    g_toMove = 0                            #-- side to move, 0 or 8, 0 = black, 8 = white
    g_castleRights = 0                      #-- bitmask representing castling rights, 1 = wk, 2 = wq, 4 = bk, 8 = bq
    g_enPassentSquare = 0
    g_baseEval = 0
    g_hashKeyLow = 0
    g_hashKeyHigh = 0
    g_inCheck = False
    
    # -- Utility variables
    g_moveCount = 0
    g_moveUndoStack = []     #-- new Array()
    
    g_move50 = 0
    g_repMoveStack = []      #-- new Array()
    
    g_hashSize = (1 << 22)
    
    g_hashMask = g_hashSize - 1
    g_hashTable = [None for x in range(g_hashSize)]      #--new Array(g_hashSize)
    
    g_killers = [[0,0] for x in range(128)]              #--new Array(128x2)

    historyTable = [[0 for x in range(256)] for x in range(32)]        #-- new Array(32x256)
    
    g_zobristLow  = [[0 for x in range(16)] for x in range(256)]      #-- new Array(256x16)
    g_zobristHigh = [[0 for x in range(16)] for x in range(256)]      #-- new Array(256x16)
    g_zobristBlackLow = 0
    g_zobristBlackHigh = 0
    
    # -- Evaulation variables
    g_mobUnit = [[0 for x in range(256)] for x in range(2)]
    
    hashflagAlpha = 1
    hashflagBeta = 2
    hashflagExact = 3
    
    # --
    # -- for searching code
    # --
    
    g_nodeCount = 0
    g_qNodeCount= 0
    g_searchValid = True
    
    minEval = -2000000
    maxEval = 2000000
    
    minMateBuffer = minEval + 2000
    maxMateBuffer = maxEval - 2000
    
    materialTable = [0, 800, 3350, 3450, 5000, 9750, 600000]
    
    pawnAdj = [
    0, 0, 0, 0, 0, 0, 0, 0,
    -25, 105, 135, 270, 270, 135, 105, -25,
    -80, 0, 30, 176, 176, 30, 0, -80,
    -85, -5, 25, 175, 175, 25, -5, -85,
    -90, -10, 20, 125, 125, 20, -10, -90,
    -95, -15, 15, 75, 75, 15, -15, -95,
    -100, -20, 10, 70, 70, 10, -20, -100,
    0, 0, 0, 0, 0, 0, 0, 0 ]
    
    knightAdj = [
    -200, -100, -50, -50, -50, -50, -100, -200,
    -100, 0, 0, 0, 0, 0, 0, -100,
    -50, 0, 60, 60, 60, 60, 0, -50,
    -50, 0, 30, 60, 60, 30, 0, -50,
    -50, 0, 30, 60, 60, 30, 0, -50,
    -50, 0, 30, 30, 30, 30, 0, -50,
    -100, 0, 0, 0, 0, 0, 0, -100,
    -200, -50, -25, -25, -25, -25, -50, -200 ]
    
    bishopAdj = [
    -50,-50,-25,-10,-10,-25,-50,-50,
    -50,-25,-10,  0,  0,-10,-25,-50,
    -25,-10,  0, 25, 25,  0,-10,-25,
    -10,  0, 25, 40, 40, 25,  0,-10,
    -10,  0, 25, 40, 40, 25,  0,-10,
    -25,-10,  0, 25, 25,  0,-10,-25,
    -50,-25,-10,  0,  0,-10,-25,-50,
    -50,-50,-25,-10,-10,-25,-50,-50 ]
    
    rookAdj = [
    -60, -30, -10, 20, 20, -10, -30, -60,
    40,  70,  90,120,120,  90,  70,  40,
    -60, -30, -10, 20, 20, -10, -30, -60,
    -60, -30, -10, 20, 20, -10, -30, -60,
    -60, -30, -10, 20, 20, -10, -30, -60,
    -60, -30, -10, 20, 20, -10, -30, -60,
    -60, -30, -10, 20, 20, -10, -30, -60,
    -60, -30, -10, 20, 20, -10, -30, -60 ]
    
    kingAdj = [
    50, 150, -25, -125, -125, -25, 150, 50,
    50, 150, -25, -125, -125, -25, 150, 50,
    50, 150, -25, -125, -125, -25, 150, 50,
    50, 150, -25, -125, -125, -25, 150, 50,
    50, 150, -25, -125, -125, -25, 150, 50,
    50, 150, -25, -125, -125, -25, 150, 50,
    50, 150, -25, -125, -125, -25, 150, 50,
    150, 250, 75, -25, -25, 75, 250, 150 ]
    
    emptyAdj = [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0 ]
    
    pieceSquareAdj = [[0 for x in range(256)] for x in range(8)]     #-- new Array(8x256)
    
    # -- Returns the square flipped
    flipTable = [0 for x in range(256)]            #-- new Array(256)
    
    g_pieceIndex = [0 for x in range(256)]         #-- new Array(256)
    g_pieceList = [0 for x in range(2 * 8 * 16)]   #-- new Array(2 * 8 * 16)
    g_pieceCount = [0 for x in range(2 * 8)]       #-- new Array(2 * 8)
    
    PieceCharList = [" ", "p", "n", "b", "r", "q", "k", " "]

    def tonumber(s):
      if(len(s)==0 or ("0123456789-.").find(s[0],0)<0):
        return 0
      else:
        return int(s)
    
    # --
    def FormatSquare(square):
      return chr( ord("a") + (square & 0xF) - 4) + str((9 - (square >> 4)) + 1)
      
    # --
    # --
    def deFormatSquare(at):
      
      h = ord(at[0]) - ord("a") + 4
      v = 9 - ( ord(at[1]) - ord("0") -1 )
      
      return ( h | ( v << 4 ) )
      
      
    # --
    # --
    def iif(ask, onTrue, onFalse):
      retval = onFalse
      if( ask ):
        retval = onTrue
        
      return retval
      
    # --
    # --
    def GetFen():

      global  colorWhite, g_board, g_castleRights, g_enPassentSquare, PieceCharList
      
      result = ""
      row = 0
      empty = 0
      col = 0
      piece = 0
      
      while(row < 8):
        if (row != 0):
          result +=  '/'
          
        empty = 0
        col = 0
        while(col < 8):
          piece = g_board[((row + 2) << 4) + col + 4]
          if (piece == 0):
            empty = empty + 1
            
          else:
            if (empty != 0):
              result +=  str(empty)
              
            empty = 0
            pieceChar = PieceCharList[(piece & 0x7)]
            if( (piece & colorWhite) != 0):
              result=result + pieceChar.upper()
            else:
              result=result + pieceChar
              
            
          
          col=col+1
          
        if (empty != 0):
          result +=  str( empty )
          
        row += 1
        
      
      result +=  iif(colorWhite>0," w","b")
      result +=  " "
      if (g_castleRights == 0):
        result +=  "-"
      else:
        if ((g_castleRights & 1) != 0):
          result +=  "K"
          
        if ((g_castleRights & 2) != 0):
          result +=  "Q"
          
        if ((g_castleRights & 4) != 0):
          result +=  "k"
          
        if ((g_castleRights & 8) != 0):
          result +=  "q"

      
      result +=  " "
      if (g_enPassentSquare < 1):
        result +=  '-'
      else:
        result +=  FormatSquare(g_enPassentSquare)
        
      
      return result
      
      
    # --
    
    # --
    def InitializeEval():

      global  piecePawn, pieceKnight, pieceBishop, pieceRook, pieceQueen, pieceKing, g_mobUnit

      friend = 0
      enemy = 0
      
      i = 0
      while(i<2):
        enemy = iif( i == 0, 0x10, 8 )
        friend = iif( i == 0, 8, 0x10 )
        g_mobUnit[i][0] = 1
        g_mobUnit[i][0x80] = 0
        g_mobUnit[i][(enemy | piecePawn)] = 1
        g_mobUnit[i][(enemy | pieceBishop)] = 1
        g_mobUnit[i][(enemy | pieceKnight)] = 1
        g_mobUnit[i][(enemy | pieceRook)] = 1
        g_mobUnit[i][(enemy | pieceQueen)] = 1
        g_mobUnit[i][(enemy | pieceKing)] = 1
        g_mobUnit[i][(friend | piecePawn)] = 0
        g_mobUnit[i][(friend | pieceBishop)] = 0
        g_mobUnit[i][(friend | pieceKnight)] = 0
        g_mobUnit[i][(friend | pieceRook)] = 0
        g_mobUnit[i][(friend | pieceQueen)] = 0
        g_mobUnit[i][(friend | pieceKing)] = 0
        i += 1
      
    # --
    
    # --
    class HashEnts:

      lock = 0
      value = 0
      flags = 0
      hashDepth = 0
      bestMove = 0

    def HashEntry(hs, hlock, hvalue, hflags, hhashDepth, hbestMove):

      hs.lock = hlock
      hs.value = hvalue
      hs.flags = hflags
      hs.hashDepth = hhashDepth
      hs.bestMove = hbestMove
      return
      
    # --
    
    # --
    def StoreHash(value, flags, ply, move, depth):

      global  g_hashKeyLow, g_hashKeyHigh, g_hashMask, g_hashTable
      global  minMateBuffer, maxMateBuffer

      hs = HashEnts()

      if (value >= maxMateBuffer):
        value +=  depth
      else:
        if (value <= minMateBuffer):
          value -=  depth
          
      HashEntry(hs, g_hashKeyHigh, value, flags, ply, move)  
      g_hashTable[(g_hashKeyLow & g_hashMask)] = hs
      
    # --
    
    # --
    class HasResult:

      hashKeyLow = 0
      hashKeyHigh = 0

    def SetHash():

      global  g_board, g_toMove, g_zobristLow, g_zobristHigh, g_zobristBlackLow, g_zobristBlackHigh

      result = HasResult()
      piece = 0
      result.hashKeyLow = 0
      result.hashKeyHigh = 0
      i = 0
      while(i<256):
        piece = g_board[i]
        if ((piece & 0x18)>0):

          result.hashKeyLow = ( result.hashKeyLow ^ g_zobristLow[i][(piece & 0xF)] )
          result.hashKeyHigh = ( result.hashKeyHigh ^ g_zobristHigh[i][(piece & 0xF)] )

        i += 1 
        
      
      if (g_toMove==0):
        result.hashKeyLow = ( result.hashKeyLow ^  g_zobristBlackLow )
        result.hashKeyHigh = ( result.hashKeyHigh ^  g_zobristBlackHigh )
        
      
      return result
      
    # --
    # --
    def MakeTable(kI, table):

      global  pieceSquareAdj

      row = 0
      col = 0
        
      while(row<8):
        col = 0
        while(col<8):
          pieceSquareAdj[kI][MakeSquare(row, col)] = table[((row * 8) + col)]
          col += 1
        row += 1  
        
      return
      
    # --
    
    # --
    def MakeSquare(row, column):
      return ( ((row + 2) << 4) | (column + 4) )
      
    # --
    # --
    def InitializeFromFen(fen):

      global  colorBlack, colorWhite, piecePawn, pieceKnight
      global  pieceBishop, pieceRook, pieceQueen, pieceKing
      global  g_board, g_toMove, g_castleRights, g_enPassentSquare
      global  g_baseEval, g_hashKeyLow, g_hashKeyHigh
      global  g_inCheck, g_move50, materialTable
      global  pieceSquareAdj, flipTable, g_pieceList
      
      chunks = []
      i = 0
      j = 0
      row = 0
      col = 0
      pieces = 0
      c = " "
      isBlack = False
      piece = 0
      fen2 = fen
      s1 = 0
      
      while( len(fen2)>0):
        s1 = fen2.find( " " );
        if( s1 < 0 ):
          chunks.append( fen2 )
          fen2 = ""
        else:
          chunks.append( fen2[0: s1] )
          fen2 = fen2[(s1+1):]
      
      i = 0
      while(i<256):
        
        g_board[i] = 0x80
        i += 1
  
      
      row = 0
      col = 0
      
      pieces = chunks[0]
      i = 0
      while(i<len(pieces)):
        
        c = pieces[i];
        
        if (c == '/'):
          row += 1
          col = 0
        else:
          if ( c >= '0' and c <= '9' ):
            j = 0
            while(j<tonumber(c)):
              g_board[((row + 2) * 0x10) + (col + 4)] = 0
              col += 1
              j += 1
            
          else:
            isBlack = (c >= 'a' and c <= 'z')
            piece = iif(isBlack, colorBlack, colorWhite)
            
            if (not isBlack):
              c = ( pieces[i].lower() )
              
            if(c=='p'):
              piece = (piece | piecePawn)
              
            if(c=='b'):
              piece = (piece | pieceBishop)
              
            if(c=='n'):
              piece = (piece | pieceKnight)
              
            if(c=='r'):
              piece = (piece | pieceRook)
              
            if(c=='q'):
              piece = (piece | pieceQueen)
              
            if(c=='k'):
              piece = (piece | pieceKing)
              
            
            g_board[((row + 2) * 0x10) + (col + 4)] = piece
            col += 1

        i += 1    
            
      
      InitializePieceList()
      
      g_toMove = iif( chunks[1] == 'w' , colorWhite , 0 )
      
      g_castleRights = 0
      if((chunks[2]).find ('K') >= 0 ):
        g_castleRights = (g_castleRights | 1 )

      if((chunks[2]).find ('Q') >= 0 ):        
        g_castleRights = (g_castleRights | 2 )

      if((chunks[2]).find ('k') >= 0 ):        
        g_castleRights = (g_castleRights | 4 )
        
      if((chunks[2]).find ('q') >= 0 ):
        g_castleRights = (g_castleRights | 8 )
        
      
      g_enPassentSquare = -1
      if((chunks[3]).find ('-') < 0 ):
        g_enPassentSquare = deFormatSquare(chunks[3])
      
      
      hashResult = SetHash()
      g_hashKeyLow = hashResult.hashKeyLow
      g_hashKeyHigh = hashResult.hashKeyHigh
      
      g_baseEval = 0
      i = 0
      while(i<256):
        if ((g_board[i] & colorWhite)>0):
          g_baseEval +=  pieceSquareAdj[( g_board[i] & 0x7)][i]
          g_baseEval +=  materialTable[(g_board[i] & 0x7)]
        else:
          if ((g_board[i] & colorBlack)>0):
            g_baseEval -=  pieceSquareAdj[(g_board[i] & 0x7)][flipTable[i]]
            g_baseEval -=  materialTable[(g_board[i] & 0x7)]
        i += 1

      
      if (g_toMove==0):
        g_baseEval = -g_baseEval
 
      g_move50 = 0
      
      g_inCheck = IsSquareAttackable(g_pieceList[ ( (g_toMove | pieceKing) << 4)], 8 - g_toMove)
      
      return      
    
    # --
    
    # --
    def IsSquareAttackableFrom(target, sfrom):

      global  g_vectorDelta, g_vectdelta, g_board

      index = sfrom - target + 128
      piece = g_board[sfrom]
      inc = 0

      if ( ( g_vectorDelta[index][ ( (piece >> 3) & 1)] & (1 << (piece & 0x7)) )>0 ):
       
        # -- Yes, this square is pseudo-attackable.  Now, check for real attack
        inc = g_vectdelta[index]

        while(True):
          sfrom += inc
          if (sfrom == target):
            return True
            
          if (g_board[sfrom] != 0):
            break
      return False
      
    # --
    
    # --
    def IsSquareAttackable(target, color):

      global  colorBlack, colorWhite, g_board, g_pieceList

      # -- Attackable by pawns?
      inc = iif( color>0 , -16 , 16 )
      pawn = ( iif(color>0 , colorWhite , colorBlack) | 1 )
      index = 0
      square = 0
      i = 0
      
      if (g_board[target - (inc - 1)] == pawn):
        return True
        
      if (g_board[target - (inc + 1)] == pawn):
        return True
        
      
      # -- Attackable by pieces?
      i = 2
      while(i<7):
        index = ( (color | i) << 4 )
        square = g_pieceList[index]
        while (square != 0):
          if (IsSquareAttackableFrom(target, square)):
            return True
            
          index += 1
          square = g_pieceList[index]
        i += 1  
        
      return False
      
    # --
    
    # --
    def IsHashMoveValid(hashMove):

      global  colorWhite, piecePawn, pieceKing
      global  moveflagEPC, moveflagPromotion, g_board, g_toMove

      sfrom = ( hashMove & 0xFF )
      sto = ( (hashMove >> 8) & 0xFF )
      dir = sto - sfrom
      ourPiece = g_board[sfrom]
      pieceType = ( ourPiece & 0x7 )
      row = 0
      
      if (pieceType < piecePawn or pieceType > pieceKing):
        return False
        
      # -- Can't move a piece we don't control
      if (g_toMove != (ourPiece & 0x8)):
        return False
        
      
      # -- Can't move to a square that has something of the same color
      if (g_board[sto] != 0 and (g_toMove == (g_board[sto] & 0x8))):
        return False
        
      
      if (pieceType == piecePawn):
        if ( ( hashMove & moveflagEPC )>0 ):
          return False
          
        # -- Valid moves are push, capture, double push, promotions
        if ((g_toMove == colorWhite) != (dir < 0)) :
          # -- Pawns have to move in the right direction
          return False
          
        
        row = ( sto & 0xF0 )
        if (((row == 0x90 and (g_toMove == 0)) or (row == 0x20 and g_toMove>0)) != ((hashMove & moveflagPromotion)>0) ):
          # -- Handle promotions
          return False
          
        
        if (dir == -16 or dir == 16):
          # -- White/Black push
          return (g_board[sto] == 0)
        else:
          if (dir == -15 or dir == -17 or dir == 15 or dir == 17):
            # -- White/Black capture
            return (g_board[sto] != 0)
          else:
            if (dir == -32):
              # -- Double white push
              if (row != 0x60):
                return False
                
              if (g_board[sto] != 0):
                return False
                
              if (g_board[(sfrom - 16)] != 0):
                return False
                
            else:
              if (dir == 32):
                # -- Double black push
                if (row != 0x50):
                  return False
                  
                if (g_board[sto] != 0):
                  return False
                  
                if (g_board[(sfrom + 16)] != 0):
                  return False
                  
              else:
                return False
        
        
        return True
        
      else:
        # -- This validates that this piece type can actually make the attack
        if ( ( hashMove >> 16)>0 ):
          return False
          
        return IsSquareAttackableFrom(sto, sfrom)
        
      
    # --
    
    # --
    def IsRepDraw():

      global  g_hashKeyLow, g_moveCount, g_move50, g_repMoveStack

      i = g_moveCount - 5
      stop = g_moveCount - 1 - g_move50
      stop = iif( stop < 0 , 0 , stop )
      
      while ( i >= stop ):
        if (g_repMoveStack[i] == g_hashKeyLow):
          return True
        i -=  2
        
      return False
      
    # --
    
    
    class MovePckr:

      hashMove = 0
      depth = 0
      killer1 = 0
      killer2 = 0
      
      moves = []             #-- new Array()
      losingCaptures = []
      mCount = 0
      atMove = -1
      mScores = []
      stage = 0

    def MovePicker(mp, phashMove, pdepth, pkiller1, pkiller2):
      
      mp.hashMove = phashMove
      mp.depth = pdepth
      mp.killer1 = pkiller1
      mp.killer2 = pkiller2  

      mp.moves = []             #-- new Array()
      mp.losingCaptures = []
      mp.mCount = 0
      mp.atMove = -1
      mp.mScores = []
      mp.stage = 0      
    
    def MPnextMove(mp):

      global  g_board

      i = 0
      j = 0
      captured = 0
      pieceType = 0
      bestMove = 0
      tmpMove = 0
      tmpScore = 0
      candidateMove = 0
      
      mp.atMove +=  1
      
      if (mp.atMove == mp.mCount):
        
        mp.stage +=  1
        if (mp.stage == 1):

          if ((mp.hashMove != None) and IsHashMoveValid(mp.hashMove)):
            mp.moves.append( mp.hashMove )
            mp.mCount = 1
            
          if (mp.mCount != 1):
            mp.hashMove = None
            mp.stage +=  1
            
        if (mp.stage == 2):
          GenerateCaptureMoves(mp.moves)

          mp.mCount = len( mp.moves )
          mp.mScores = [None for x in range(mp.mCount)]      #-- new Array(this.moveCount)
          # -- Move ordering
          i = mp.atMove
          while( len( mp.mScores )<len( mp.moves ) ):
            mp.mScores.append(None)
          while(i<mp.mCount):
            captured = ( g_board[ ( (mp.moves[i] >> 8) & 0xFF)] & 0x7 )
            pieceType = ( g_board[ ( mp.moves[i] & 0xFF)] & 0x7 )

            mp.mScores[i] = (captured << 5) - pieceType
            i += 1
            
          # -- No moves, onto next stage
          if (mp.atMove == mp.mCount):
            mp.stage +=  1
          
          
        if (mp.stage == 3):
          if (IsHashMoveValid(mp.killer1) and (mp.killer1 != mp.hashMove)):
            mp.moves.append( mp.killer1 )
            mp.mCount = len(mp.moves)
          else:
            mp.killer1 = 0
            mp.stage +=  1
            
          
        if (mp.stage == 4):
          if (IsHashMoveValid(mp.killer2) and (mp.killer2 != mp.hashMove)):
            mp.moves.append( mp.killer2 )
            mp.mCount = len(mp.moves)
          else:
            mp.killer2 = 0
            mp.stage +=  1
            
          
        
        if (mp.stage == 5):

          GenerateAllMoves(mp.moves)
          mp.mCount = len(mp.moves)
          # -- Move ordering

          while( len(mp.mScores)<mp.mCount ):
            mp.mScores.append(None)

          i = mp.atMove
          while(i<mp.mCount):

            mp.mScores[i] = ScoreMove(mp.moves[i])
            i += 1
            
          # -- No moves, onto next stage
          if (mp.atMove == mp.mCount):
            mp.stage +=  1
            
          
        
        if (mp.stage == 6):
          # -- Losing captures
          if ( len(mp.losingCaptures)>0 ):
            i = 0
            while(i<len( mp.losingCaptures )):
              mp.moves.append( mp.losingCaptures[i] )
              i += 1

            while( len(mp.mScores)<len(mp.moves) ):
              mp.mScores.append(None)

            i = mp.atMove              
            while(i<mp.mCount):

              mp.mScores[i] = ScoreMove(mp.moves[i])
              i += 1
              
            mp.mCount = len(mp.moves)
            
          # -- No moves, onto next stage
          if (mp.atMove == mp.mCount):
            mp.stage +=  1
            
        
        if (mp.stage == 7):
          return 0
          
      
      bestMove = mp.atMove
      j = mp.atMove + 1
      while(j<mp.mCount):
        if( len(mp.mScores)<(j+1) or mp.mScores[j]==None ):
          break

        if (mp.mScores[j] > mp.mScores[bestMove]):
          bestMove = j
        j += 1
          
      
      if (bestMove != mp.atMove):
        tmpMove = mp.moves[mp.atMove]
        mp.moves[mp.atMove] = mp.moves[bestMove]
        mp.moves[bestMove] = tmpMove
        
        tmpScore = mp.mScores[mp.atMove]
        mp.mScores[mp.atMove] = mp.mScores[bestMove]
        mp.mScores[bestMove] = tmpScore
        
      candidateMove = mp.moves[mp.atMove]
      if ((mp.stage > 1 and candidateMove == mp.hashMove) or (mp.stage > 3 and candidateMove == mp.killer1) or (mp.stage > 4 and candidateMove == mp.killer2)):
        
        return MPnextMove(mp)
        
      
      if (mp.stage == 2 and (not See(candidateMove))):
        mp.losingCaptures.append( candidateMove )
        return MPnextMove(mp)
        
      return mp.moves[mp.atMove]
      
    # --
    
    # --
    def AllCutNode(ply, depth, beta, allowNull):

      global  g_timeout, g_maxfinCnt, g_startTime, g_finCnt, pieceKnight, pieceBishop
      global  pieceRook, pieceQueen, g_board, g_toMove, g_baseEval, g_hashKeyLow
      global  g_hashKeyHigh, g_inCheck, g_hashMask, g_hashTable
      global  g_killers, historyTable, g_zobristBlackLow, g_zobristBlackHigh
      global  hashflagAlpha, hashflagBeta, hashflagExact, g_nodeCount
      global  g_searchValid, minEval, maxEval, minMateBuffer, g_pieceCount
      
      hashMove = None
      hashNode = None
      hashValue = 0
      razorMargin = 2500 + 200 * ply
      razorBeta = 0
      v = 0
      r = 0
      value = 0
      moveMade = False
      realEval = 0
      inCheck = False
      currentMove = 0
      plyToSearch = 0
      doFullSearch = True
      value = 0
      reduced = 0
      histTo = 0
      histPiece = 0
      h = 0
      mp = MovePckr()
      
      if (ply <= 0):
        return QSearch(beta - 1, beta, 0)
        
      
      if (time.perf_counter() - g_startTime > g_timeout):
        # -- Time cutoff
        g_searchValid = False
        return beta - 1
        
      
      if(g_finCnt>g_maxfinCnt):
        # -- Limit for moves
        g_searchValid = False
        return beta - 1
        
      
      g_nodeCount += 1
      
      if (IsRepDraw()):
        return 0
        
      
      # -- Mate distance pruning
      if (minEval + depth >= beta):
        return beta
        
      
      if ((maxEval - (depth + 1)) < beta):
        return (beta - 1)
        
      hashNode = g_hashTable[ ( g_hashKeyLow & g_hashMask )]
      
      if ((hashNode != None) and (hashNode.lock == g_hashKeyHigh)):
        hashMove = hashNode.bestMove
        
        if (hashNode.hashDepth >= ply):
          hashValue = hashNode.value
          
          # -- Fixup mate scores
          if (hashValue >= maxMateBuffer):
            hashValue = hashValue - depth
          else:
            if (hashValue <= minMateBuffer):
              hashValue = hashValue + depth
              
          if (hashNode.flags == hashflagExact):
            return hashValue
            
          if (hashNode.flags == hashflagAlpha and hashValue < beta):
            return hashValue
            
          if (hashNode.flags == hashflagBeta and hashValue >= beta):
            return hashValue
        
      
      # -- TODO - positional gain?
      
      if ((not g_inCheck) and allowNull and (beta > minMateBuffer) and (beta < maxMateBuffer)):
        # -- Try some razoring
        if (hashMove == None and ply < 4):
          
          if (g_baseEval < beta - razorMargin):
            razorBeta = beta - razorMargin
            v = QSearch(razorBeta - 1, razorBeta, 0)
            if (v < razorBeta):
              return v
          
        # -- TODO - static null move
        
        # -- Null move
        # -- Disable null move if potential zugzwang (no big pieces)
        if (ply > 1 and g_baseEval >= beta - iif(ply >= 4, 2500, 0) and (g_pieceCount[ (pieceBishop | g_toMove)] != 0 or g_pieceCount[ (pieceKnight | g_toMove)] != 0 or g_pieceCount[ (pieceRook | g_toMove)] != 0 or g_pieceCount[ (pieceQueen | g_toMove)] != 0)):
          r = 3 + iif(ply >= 5, 1, ply / 4)
          if (g_baseEval - beta > 1500):
            r += 1
            
          
          g_toMove = 8 - g_toMove
          g_baseEval = -g_baseEval
          g_hashKeyLow = ( g_hashKeyLow ^ g_zobristBlackLow )
          g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristBlackHigh )
          
          value = -AllCutNode(ply - r, depth + 1, -(beta - 1), False)
          
          g_hashKeyLow = ( g_hashKeyLow ^ g_zobristBlackLow )
          g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristBlackHigh )
          g_toMove = 8 - g_toMove
          g_baseEval = -g_baseEval
          
          if (value >= beta):
            return beta
        
      
      moveMade = False
      realEval = minEval
      inCheck = g_inCheck
      
      MovePicker(mp, hashMove, depth, g_killers[depth][0], g_killers[depth][1])
      
      while(True):
        
        currentMove = MPnextMove(mp)
        if (currentMove == 0):
          break
        
        
        plyToSearch = ply - 1
        
        if (MakeMove(currentMove)):
          
          doFullSearch = True
          
          if (g_inCheck):
            # -- Check extensions
            plyToSearch += 1
          else:
            
            # -- Late move reductions
            if (mp.stage == 5 and mp.atMove > 5 and ply >= 3):
              reduced = plyToSearch - iif(mp.atMove > 14, 2, 1)
              value = -AllCutNode(reduced, depth + 1, -(beta - 1), True)
              doFullSearch = (value >= beta)
  
          
          if (doFullSearch):
            value = -AllCutNode(plyToSearch, depth + 1, -(beta  - 1), True)

          
          moveMade = True
          
          UnmakeMove(currentMove)
          
          if (not g_searchValid):
            
            return beta - 1
            
          
          if (value > realEval):
            
            if (value >= beta):
              histTo = ( (currentMove >> 8) & 0xFF )
              if (g_board[histTo] == 0):
                histPiece = ( g_board[ (currentMove & 0xFF)] & 0xF )
                h = historyTable[histPiece][histTo]
                h = h + (ply * ply)
                if (h > 32767):
                  h = ( h >> 1 )
                  
                historyTable[histPiece][histTo] = h
                
                if (g_killers[depth][0] != currentMove):
                  g_killers[depth][1] = g_killers[depth][0]
                  g_killers[depth][0] = currentMove
                  
                
              
              StoreHash(value, hashflagBeta, ply, currentMove, depth)
              return value
              
            
            realEval = value
            hashMove = currentMove
        
      
      if (not moveMade):
        # -- If we have no valid moves it's either stalemate or checkmate
        if (g_inCheck):
          return (minEval + depth);            #-- Checkmate.
        else:
          return 0;                            #-- Stalemate
        
      
      StoreHash(realEval, hashflagAlpha, ply, hashMove, depth)
      
      return realEval
      
    # --
    
    # --
    def AlphaBeta(ply, depth, alpha, beta):

      global  g_board, g_hashKeyLow, g_hashKeyHigh, g_inCheck, g_hashMask
      global  g_hashTable, g_killers, historyTable, hashflagAlpha, hashflagBeta, hashflagExact
      global  g_nodeCount, g_searchValid, minEval, maxEval
      
      moveMade = False
      realEval = 0
      inCheck = False
      
      oldAlpha = alpha
      hashMove = None
      
      hashMove = None
      hashFlag = hashflagAlpha
      hashNode = None
      currentMove = 0
      value = 0
      histTo = 0
      histPiece = 0
      plyToSearch = ply - 1
      mp = MovePckr()
      
      if (ply <= 0):
        return QSearch(alpha, beta, 0)
        
      
      g_nodeCount += 1
      
      if (depth > 0 and IsRepDraw()):
        return 0
        
      
      # -- Mate distance pruning
      alpha = iif( (alpha < minEval + depth) , alpha , minEval + depth )
      beta = iif( (beta > maxEval - (depth + 1)) , beta , maxEval - (depth + 1) )
      if (alpha >= beta):
        return alpha
      
      
      hashNode = g_hashTable[ ( g_hashKeyLow & g_hashMask )]
      if (hashNode != None and hashNode.lock == g_hashKeyHigh):
        hashMove = hashNode.bestMove
        
      
      inCheck = g_inCheck
      moveMade = False
      realEval = minEval 
      
      MovePicker(mp, hashMove, depth, g_killers[depth][0], g_killers[depth][1])

      while(True):
        
        currentMove = MPnextMove(mp)
        
        if (currentMove == 0):
          break
          
        
        plyToSearch = ply - 1
        
        if (MakeMove(currentMove)):
          
          if (g_inCheck):
            plyToSearch += 1      #-- Check extensions
            
          
          if (moveMade):
            
            value = -AllCutNode(plyToSearch, depth + 1, -alpha, True)
            
            if (value > alpha):
              value = -AlphaBeta(plyToSearch, depth + 1, -beta, -alpha)
              
          else:
            value = -AlphaBeta(plyToSearch, depth + 1, -beta, -alpha)
            
          
          moveMade = True
          
          UnmakeMove(currentMove)
          
          if (not g_searchValid):
            return alpha
            
          
          if (value > realEval):
            if (value >= beta):
              histTo = ( (currentMove >> 8) & 0xFF )
              if (g_board[histTo] == 0):
                histPiece = ( g_board[ ( currentMove & 0xFF )] & 0xF )
                h = historyTable[histPiece][histTo]
                h += (ply * ply)
                if (h > 32767):
                  h = ( h >> 1 )
                  
                historyTable[histPiece][histTo] = h
                
                if (g_killers[depth][0] != currentMove):
                  g_killers[depth][1] = g_killers[depth][0]
                  g_killers[depth][0] = currentMove
                  
                
              
              StoreHash(value, hashflagBeta, ply, currentMove, depth)
              return value
              
            
            if (value > oldAlpha):
              hashFlag = hashflagExact
              alpha = value
              
            
            realEval = value
            hashMove = currentMove
        
      
      if (not moveMade):
        # -- If we have no valid moves it's either stalemate or checkmate
        if (inCheck):
          return (minEval + depth)      #-- Checkmate.
        else:
          return 0                      #-- Stalemate
        
      
      StoreHash(realEval, hashFlag, ply, hashMove, depth)
      
      return realEval
      
    # --
    
    # --
    def InitializePieceList():

      global  colorBlack, colorWhite, g_board, g_pieceIndex, g_pieceList, g_pieceCount
      
      i = 0
      j = 0
      piece = 0
      
      while(i<16):
        g_pieceCount[i] = 0
        j = 0
        while(j<16):
          # -- 0 is used as the terminator for piece lists
          g_pieceList[ ( (i << 4) | j)] = 0
          j += 1
        i += 1
          
      i = 0      
      while(i<256):
        g_pieceIndex[i] = 0
        if ( ( g_board[i] & (colorWhite | colorBlack) )>0 ):
          piece = ( g_board[i] & 0xF )
          
          g_pieceList[( (piece << 4) | g_pieceCount[piece])] = i
          g_pieceIndex[i] = g_pieceCount[piece]
          g_pieceCount[piece] += 1
        i += 1          
      
    # --
    
    # -- SetSeeds for Zobrist.
    class Zobrist:
    
      N = 624
      M = 397
      MAG01 = [0x0, 0x9908b0df]
    
      mt = [0 for x in range(N)]    # -- new Array(N)
      mti = N + 1
    
    def ZbsetSeed( Zb, N0 ):

      s = 0
      Zb.mt[0]= N0
      i = 1        
      while(i<Zb.N):
        s = ( Zb.mt[(i - 1)] ^ (Zb.mt[(i - 1)] >> 26) )    # >> 30 originally
        Zb.mt[i] = ( (1812433253 * ((s & 0xffff0000) >> 16)) << 16) + 1812433253 * (s & 0x0000ffff) + i
        i += 1

      Zb.mti = Zb.N
      return
      
    def Zbnext( Zb, bits ):
      
      x = 0
      y = 0
      k = 0
      
      if( Zb.mti >= Zb.N ):
        
        while(k<(Zb.N - Zb.M)):
          x = ( (Zb.mt[k] & 0x80000000) | (Zb.mt[(k + 1)] & 0x7fffffff) )
          Zb.mt[k] = ( ( Zb.mt[(k + Zb.M)] ^ (x >> 1) ) ^ Zb.MAG01[(x & 0x1)] )
          k += 1
          
        k = Zb.N - Zb.M        
        while(k<(Zb.N - 1)):
          x = ( (Zb.mt[k] & 0x80000000) | (Zb.mt[(k + 1)] & 0x7fffffff) )
          Zb.mt[k] = ( ( Zb.mt[k + (Zb.M - Zb.N)] ^ (x >> 1) ) ^ Zb.MAG01[(x & 0x1)] )
          k += 1
          
        x = ( (Zb.mt[(Zb.N - 1)] & 0x80000000) | (Zb.mt[1] & 0x7fffffff) )
        Zb.mt[(Zb.N - 1)] = ( ( Zb.mt[(Zb.M - 1)] ^ (x >> 1) ) ^ Zb.MAG01[(x & 0x1)] )
        Zb.mti = 0
        
      
      y = Zb.mt[Zb.mti]
      Zb.mti += 1
      y = ( y ^ ( y >> 11 ) )
      y = ( y ^ ( (y << 7) & 0x9d2c5680 ) )
      y = ( y ^ ( (y << 15) & 0xefc60000 ) )
      y = ( y ^ ( y >> 18 ) )
      y = ( (y >> (32 - bits)) & 0xFFFFFFFF )
      return y
      
    # --
    
    # --
    def ResetGame():

      global  colorWhite, piecePawn, pieceKnight, pieceBishop
      global  pieceRook, pieceQueen, pieceKing, g_vectorDelta, g_vectdelta, g_bishopDeltas
      global  g_knightDeltas, g_rookDeltas, g_queenDeltas, g_hashSize, g_hashTable, g_killers
      global  historyTable, g_zobristLow, g_zobristHigh, g_zobristBlackLow
      global  g_zobristBlackHigh, pawnAdj, knightAdj, bishopAdj
      global  rookAdj, kingAdj, emptyAdj, pieceSquareAdj, flipTable

      i = 0
      j = 0
      k = 0
      row = 0
      col = 0
      square = 0

      pieceDeltas = [ [], [], g_knightDeltas, g_bishopDeltas, g_rookDeltas, g_queenDeltas, g_queenDeltas ]

      index = 0
      dir = 0
      target = 0
      flip = -1
      mt = Zobrist()

      ZbsetSeed( mt, 0x1badf00d )
      
      i = 0
      while(i<256):
        j = 0
        while(j<16):
          g_zobristLow[i][j] = Zbnext(mt,32)
          g_zobristHigh[i][j] = Zbnext(mt,32)

          j += 1
        i += 1  
        
      g_zobristBlackLow = Zbnext(mt,32)
      g_zobristBlackHigh = Zbnext(mt,32)

      row = 0
      while(row<8):
        col = 0
        while(col<8):
          square = MakeSquare(row , col)
          flipTable[square] = MakeSquare(7 - row , col)
          col += 1
        row += 1
      
      MakeTable(piecePawn, pawnAdj)
      MakeTable(pieceKnight, knightAdj)
      MakeTable(pieceBishop, bishopAdj)
      MakeTable(pieceRook, rookAdj)
      MakeTable(pieceQueen, emptyAdj)
      MakeTable(pieceKing, kingAdj)

  
      # -- Initialize the vector delta table
      row = 0
      while(row < 0x80):
        col = 0
        while(col < 0x8):

          square = (row | col)
          
          # -- Pawn moves
          index = square - (square - 17) + 128
          g_vectorDelta[index][(colorWhite >> 3)] |= (1 << piecePawn)
          index = square - (square - 15) + 128
          g_vectorDelta[index][(colorWhite >> 3)] |= (1 << piecePawn)
          
          index = square - (square + 17) + 128
          g_vectorDelta[index][0] |= (1 << piecePawn)
          index = square - (square + 15) + 128
          g_vectorDelta[index][0] |= (1 << piecePawn)
         
          i = pieceKnight
          while(i<=pieceKing):
            dir = 0
            while(dir < len( pieceDeltas[i]) ):
              target = square + pieceDeltas[i][dir]
              while ((target & 0x88)==0):
                index = square - target + 128

                g_vectorDelta[index][(colorWhite >> 3)] |= (1 << i)
                g_vectorDelta[index][0] |= (1 << i)
                
                flip = -1
                if (square < target):
                  flip = 1
                  
                if ((square & 0xF0) == (target & 0xF0)):
                  # -- On the same row
                  g_vectdelta[index] = flip * 1
                else:
                  if ((square & 0x0F) == (target & 0x0F)):
                    # -- On the same column
                    g_vectdelta[index] = flip * 16
                  else:
                    if ((square % 15) == (target % 15)):
                      g_vectdelta[index] = flip * 15
                    else:
                      if ((square % 17) == (target % 17)):
                        g_vectdelta[index] = flip * 17
                  
                
                if (i == pieceKnight):
                  g_vectdelta[index] = pieceDeltas[i][dir]
                  break
                  
                
                if (i == pieceKing):
                  break
                  
                
                target +=  pieceDeltas[i][dir]
                
              
              dir += 1
              
            i += 1  
            
          col += 1
          
        row += 0x10
      
    # --
    
    # --
    def Search(maxPly):

      global  g_startTime, g_finCnt, g_foundmove, g_hashKeyLow, g_hashMask
      global  g_hashTable, g_nodeCount, g_qNodeCount, g_searchValid, minEval, maxEval
      
      alpha = minEval
      beta = maxEval
      
      bestMove = 0
      value = 0
      i = 1
      tmp = 0
      
      g_nodeCount = 0
      g_qNodeCount = 0
      g_searchValid = True
      g_foundmove = 0
      
      g_finCnt = 0
      g_startTime = time.perf_counter()
      
      while( i <= maxPly and g_searchValid ):
        tmp = AlphaBeta(i , 0, alpha, beta)
        if (not g_searchValid):
          break
          
        
        value = tmp
        
        if (value > alpha and value < beta):
          alpha = value - 500
          beta = value + 500
          
          if (alpha < minEval):
            alpha = minEval
            
          if (beta > maxEval):
            beta = maxEval
            
        else:
          if (alpha != minEval):
            alpha = minEval
            beta = maxEval
            i -= 1
          
        
        if (g_hashTable[(g_hashKeyLow & g_hashMask)] != None):
          bestMove = g_hashTable[(g_hashKeyLow & g_hashMask)].bestMove
          
        
        finishPlyCallback(bestMove, value, i)
        
        i += 1

      finishMoveCallback(bestMove, value, i - 1)
      
    # --
    
    # --
    def PawnEval(color):

      global  g_pieceList

      pieceIdx = ( (color | 1) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      
      while (sfrom != 0):
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
    # --
    
    # --
    def Mobility(color):

      global  g_board, g_mobUnit, g_pieceList

      result = 0
      sfrom = 0
      mob = 0
      pieceIdx = 0
      enemy = iif(color == 8, 0x10, 0x8 )
      mobUnit = iif(color == 8, g_mobUnit[0], g_mobUnit[1] )
      
      # -- Knight mobility
      mob = -3
      pieceIdx = ( (color | 2) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      
      while (sfrom != 0):
        mob +=  mobUnit[g_board[(sfrom + 31)]]
        mob +=  mobUnit[g_board[(sfrom + 33)]]
        mob +=  mobUnit[g_board[(sfrom + 14)]]
        mob +=  mobUnit[g_board[(sfrom - 14)]]
        mob +=  mobUnit[g_board[(sfrom - 31)]]
        mob +=  mobUnit[g_board[(sfrom - 33)]]
        mob +=  mobUnit[g_board[(sfrom + 18)]]
        mob +=  mobUnit[g_board[(sfrom - 18)]]
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      result +=  (65 * mob)
      
      # -- Bishop mobility
      mob = -4
      pieceIdx = ( (color | 3) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        mob = AdjMob( sfrom, -15, mob, enemy )
        mob = AdjMob( sfrom, -17, mob, enemy )
        mob = AdjMob( sfrom, 15, mob, enemy )
        mob = AdjMob( sfrom, 17, mob, enemy )
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      result +=  ( 50 * mob )
      
      # -- Rook mobility
      mob = -4
      pieceIdx = ( (color | 4) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        mob = AdjMob( sfrom, -1, mob, enemy )
        mob = AdjMob( sfrom, 1, mob, enemy )
        mob = AdjMob( sfrom, -16, mob, enemy )
        mob = AdjMob( sfrom, 16, mob, enemy )
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      result +=  ( 25 * mob )
      
      # -- Queen mobility
      mob = -2
      pieceIdx = ( (color | 5) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        mob = AdjMob( sfrom, -15, mob, enemy )
        mob = AdjMob( sfrom, -17, mob, enemy )
        mob = AdjMob( sfrom, 15, mob, enemy )
        mob = AdjMob( sfrom, 17, mob, enemy )
        mob = AdjMob( sfrom, -1, mob, enemy )
        mob = AdjMob( sfrom, 1, mob, enemy )
        mob = AdjMob( sfrom, -16, mob, enemy )
        mob = AdjMob( sfrom, 16, mob, enemy )
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      result +=  ( 22 * mob )
      
      return result
      
    # --
    
    # --
    def AdjMob(sfrom, dto, mob, enemy ):

      global  g_board

      sto=sfrom + dto
      mb=mob
      while (g_board[sto] == 0):
        sto += dto
        mb += 1
        
      if ( (g_board[sto] & enemy)>0 ):
        mb += 1
        
      return mb
      
    # --
    
    # --
    def Evaluate():

      global  colorWhite, pieceBishop, pieceQueen, pieceKing
      global  g_toMove, g_baseEval, pieceSquareAdj, flipTable, g_pieceList, g_pieceCount

      curEval = g_baseEval

      mobility = Mobility(8) - Mobility(0)
      
      evalAdjust = 0
      # -- Black queen gone, then cancel white's penalty for king movement
      if (g_pieceList[ (pieceQueen << 4)] == 0):
        evalAdjust -=  pieceSquareAdj[pieceKing][g_pieceList[ ( (colorWhite | pieceKing) << 4)]]
        
      # -- White queen gone, then cancel black's penalty for king movement
      if (g_pieceList[ ( (colorWhite | pieceQueen) << 4)] == 0):
        evalAdjust +=  pieceSquareAdj[pieceKing][flipTable[g_pieceList[(pieceKing << 4)]]]
      
      # -- Black bishop pair
      if (g_pieceCount[pieceBishop] >= 2):
        evalAdjust -=  500
        
      # -- White bishop pair
      if (g_pieceCount[ (pieceBishop | colorWhite)] >= 2):
        evalAdjust +=  500
        
      
      if (g_toMove == 0):
        # -- Black
        curEval -=  mobility
        curEval -=  evalAdjust
      else:
        curEval +=  mobility
        curEval +=  evalAdjust
        
      
      return curEval
      
    # --
    
    # --
    def ScoreMove(move):

      global  g_board, historyTable

      moveTo = ( (move >> 8) & 0xFF )
      captured = ( g_board[moveTo] & 0x7 )
      piece = g_board[ (move & 0xFF) ]
      score = 0
      pieceType = ( piece & 0x7 )
      if (captured != 0):
        score = (captured << 5) - pieceType
      else:
        score = historyTable[ (piece & 0xF) ][moveTo]
      return score
      
    # --
    
    # --
    def QSearch(alpha, beta, ply):

      global  g_board, g_inCheck, g_qNodeCount, minEval
      
      g_qNodeCount += 1
      
      realEval = iif( g_inCheck, (minEval + 1), Evaluate() )
      
      if (realEval >= beta):
        return realEval
        
      
      if (realEval > alpha):
        alpha = realEval
        
      
      moves = []      #-- new Array()
      moveScores = []      #-- new Array()
      wasInCheck = g_inCheck
      i = 0
      j = 0
      captured = 0
      pieceType = 0
      bestMove = 0
      tmpMove = 0
      tmpScore = 0
      value = 0
      checking = False
      brk = False
      
      if (wasInCheck):
        # -- TODO: Fast check escape generator and fast checking moves generator
        GenerateCaptureMoves(moves)
        GenerateAllMoves(moves)

        moveScores = [None for x in range( len( moves ) )]
        
        while(i<len( moves )):

          moveScores[i] = ScoreMove(moves[i])
          i += 1
          
      else:
        GenerateCaptureMoves(moves)
        
        moveScores = [None for x in range( len( moves ) )]

        while(i<len( moves )):
          captured = ( g_board[ ( (moves[i] >> 8) & 0xFF)] & 0x7 )
          pieceType = ( g_board[ ( moves[i] & 0xFF )] & 0x7 )
          
          moveScores[i] = (captured << 5) - pieceType
          i += 1          
        
        
      i=0
      while(i<len( moves )):
        
        bestMove = i
        j = len( moves )-1
        while(j>i):
          if (moveScores[j] > moveScores[bestMove]):
            bestMove = j
          j -= 1
            
        
        tmpMove = moves[i]
        moves[i] = moves[bestMove]
        moves[bestMove] = tmpMove
        
        tmpScore = moveScores[i]
        moveScores[i] = moveScores[bestMove]
        moveScores[bestMove] = tmpScore

        if( (wasInCheck or See(moves[i])) and MakeMove(moves[i])):

          value = -QSearch(-beta, -alpha, ply - 1)
          
          UnmakeMove(moves[i])
          
          if (value > realEval):
            if (value >= beta):
              return value
              
            if (value > alpha):
              alpha = value
              
            realEval = value
            
        i += 1      
      
      
      if ((ply == 0) and (not wasInCheck)):
        moves = []
        GenerateAllMoves(moves)

        moveScores = [None for x in range( len( moves ) )]

        i = 0
        while(i<len( moves )):
          moveScores[i] = ScoreMove(moves[i])
          i += 1
          
        i = 0        
        while(i<len( moves )):
          bestMove = i
          j = len( moves )-1
          while(j>i):
            
            if (moveScores[j] > moveScores[bestMove]):
              bestMove = j
            j -= 1
          
          tmpMove = moves[i]
          moves[i] = moves[bestMove]
          moves[bestMove] = tmpMove
          
          tmpScore = moveScores[i]
          moveScores[i] = moveScores[bestMove]
          moveScores[bestMove] = tmpScore
          
          brk = False
          
          if (not MakeMove(moves[i])):
            brk = True
          else:
            
            checking = g_inCheck
            UnmakeMove(moves[i])
            
            if (not checking):
              brk = True
            else:
              
              if (not See(moves[i])):
                brk = True
          
          if(not brk):
            
            MakeMove(moves[i])
            
            value = -QSearch(-beta, -alpha, ply - 1)
            
            UnmakeMove(moves[i])
            
            if (value > realEval):
              if (value >= beta):
                return value
                
              
              if (value > alpha):
                alpha = value
                
              
              realEval = value
              
          i += 1            

      return realEval
      
    # --

    # --
    class UndoHist:

      ep = 0
      castleRights = 0
      inCheck = False
      baseEval = 0
      hashKeyLow = 0
      hashKeyHigh = 0
      move50 = 0
      captured = 0
    
    # --
    def UndoHistory(ud, uep, ucastleRights, uinCheck, ubaseEval, uhashKeyLow, uhashKeyHigh, umove50, ucaptured):

      ud.ep = uep
      ud.castleRights = ucastleRights
      ud.inCheck = uinCheck
      ud.baseEval = ubaseEval
      ud.hashKeyLow = uhashKeyLow
      ud.hashKeyHigh = uhashKeyHigh
      ud.move50 = umove50
      ud.captured = ucaptured
      return
      
    # --
    
    # --
    def MakeMove(move):

      global  g_finCnt, pieceEmpty, piecePawn, pieceKnight, pieceBishop, pieceRook
      global  pieceQueen, pieceKing, g_castleRightsMask, moveflagEPC
      global  moveflagCastleKing, moveflagCastleQueen, moveflagPromotion
      global  moveflagPromoteKnight, moveflagPromoteQueen, moveflagPromoteBishop
      global  g_board, g_toMove, g_castleRights, g_enPassentSquare
      global  g_baseEval, g_hashKeyLow, g_hashKeyHigh, g_inCheck
      global  g_moveCount, g_moveUndoStack, g_move50, g_repMoveStack, g_zobristLow, g_zobristHigh
      global  g_zobristBlackLow, g_zobristBlackHigh, materialTable
      global  pieceSquareAdj, flipTable, g_pieceIndex, g_pieceList, g_pieceCount
      
      sme = ( g_toMove >> 3 )
      otherColor = 8 - g_toMove
      
      flags = ( move & 0xFF0000 )
      sto = ( (move >> 8) & 0xFF )
      sfrom = ( move & 0xFF )
      diff = sto - sfrom
      captured = g_board[sto]
      piece = g_board[sfrom]
      epcEnd = sto
      rook = 0
      rookIndex = 0
      newPiece = 0
      pawnType = 0
      promoteType = 0
      kingPos = 0
      theirKingPos = 0
      capturedType = 0
      lastPieceSquare = 0
      lastPawnSquare = 0
      suh = UndoHist()
      
      g_finCnt += 1
      
      if ( (flags & moveflagEPC)>0 ):
        epcEnd = iif( sme>0 , (sto + 0x10) , (sto - 0x10) )
        captured = g_board[epcEnd]
        g_board[epcEnd] = pieceEmpty
        
      UndoHistory( suh, g_enPassentSquare, g_castleRights, g_inCheck, g_baseEval, g_hashKeyLow, g_hashKeyHigh, g_move50, captured )
      
      while( g_moveCount>=len(g_moveUndoStack) ):
        g_moveUndoStack.append( None )

      g_moveUndoStack[g_moveCount] = suh;
      g_moveCount += 1
      
      g_enPassentSquare = -1
      
      if (flags>0):
        if ( ( flags & moveflagCastleKing )>0 ):
          if (IsSquareAttackable(sfrom + 1, otherColor) or IsSquareAttackable(sfrom + 2, otherColor)):
            g_moveCount -= 1
            return False
            
          
          rook = g_board[(sto + 1)]
          
          g_hashKeyLow = ( g_hashKeyLow ^ g_zobristLow[(sto + 1)][(rook & 0xF)] )
          g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristHigh[(sto + 1)][(rook & 0xF)] )
          g_hashKeyLow = ( g_hashKeyLow ^ g_zobristLow[(sto - 1)][(rook & 0xF)] )
          g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristHigh[(sto - 1)][(rook & 0xF)] )
          
          g_board[(sto - 1)] = rook
          g_board[(sto + 1)] = pieceEmpty
          
          g_baseEval -=  pieceSquareAdj[ (rook & 0x7)][ iif( sme == 0, flipTable[(sto + 1)], (sto + 1))]

          g_baseEval +=  pieceSquareAdj[ (rook & 0x7)][ iif( sme == 0, flipTable[(sto - 1)], (sto - 1))]
          
          rookIndex = g_pieceIndex[(sto + 1)]
          g_pieceIndex[(sto - 1)] = rookIndex
          g_pieceList[ ( ((rook & 0xF) << 4) | rookIndex)] = sto - 1
          
        else:
          if ( ( flags & moveflagCastleQueen)>0 ):
            if (IsSquareAttackable(sfrom - 1, otherColor) or IsSquareAttackable(sfrom - 2, otherColor)):
              g_moveCount -= 1
              return False
              
            
            rook = g_board[(sto - 2)]
            
            g_hashKeyLow = ( g_hashKeyLow ^ g_zobristLow[(sto -2)][(rook & 0xF)] )
            g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristHigh[(sto - 2)][(rook & 0xF)] )
            g_hashKeyLow = ( g_hashKeyLow ^ g_zobristLow[(sto + 1)][(rook & 0xF)] )
            g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristHigh[(sto + 1)][(rook & 0xF)] )
            
            g_board[(sto + 1)] = rook
            g_board[(sto - 2)] = pieceEmpty
            
            g_baseEval -=  pieceSquareAdj[ (rook & 0x7)][ iif( sme == 0, flipTable[(sto - 2)], (sto - 2))]

            g_baseEval +=  pieceSquareAdj[ (rook & 0x7)][ iif( sme == 0, flipTable[(sto + 1)], (sto + 1))]
            
            rookIndex = g_pieceIndex[(sto - 2)]
            g_pieceIndex[(sto + 1)] = rookIndex
            g_pieceList[ ( ((rook & 0xF) << 4) | rookIndex )] = sto + 1
        
      
      if (captured>0):
        # -- Remove our piece from the piece list
        capturedType = ( captured & 0xF )
        
        g_pieceCount[capturedType] = g_pieceCount[capturedType] - 1
        lastPieceSquare = g_pieceList[ ( (capturedType << 4) | g_pieceCount[capturedType] )]
        
        g_pieceIndex[lastPieceSquare] = g_pieceIndex[epcEnd]
        g_pieceList[ ( (capturedType << 4) | g_pieceIndex[lastPieceSquare])] = lastPieceSquare
        g_pieceList[ ( (capturedType << 4) | g_pieceCount[capturedType])] = 0
        
        
        g_baseEval +=  materialTable[ (captured & 0x7)]

        g_baseEval +=  pieceSquareAdj[ (captured & 0x7)][ iif( sme>0, flipTable[epcEnd] , epcEnd )]
        
        g_hashKeyLow = ( g_hashKeyLow ^ g_zobristLow[epcEnd][capturedType] )
        g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristHigh[epcEnd][capturedType] )
        g_move50 = 0
      else:
        if ((piece & 0x7) == piecePawn):
          if (diff < 0):
            diff = -diff
            
          if (diff > 16):
            g_enPassentSquare = iif( sme>0 , (sto + 0x10) , (sto - 0x10) )
            
          g_move50 = 0
      
      g_hashKeyLow = ( g_hashKeyLow ^ g_zobristLow[sfrom][(piece & 0xF)] )
      g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristHigh[sfrom][(piece & 0xF)] )
      g_hashKeyLow = ( g_hashKeyLow ^ g_zobristLow[sto][(piece & 0xF)] )
      g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristHigh[sto][(piece & 0xF)] )
      g_hashKeyLow = ( g_hashKeyLow ^ g_zobristBlackLow )
      g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristBlackHigh )
      
      g_castleRights = ( g_castleRights & ( g_castleRightsMask[sfrom] & g_castleRightsMask[sto] ) )
      
      g_baseEval -=  pieceSquareAdj[( piece & 0x7)][ iif( sme == 0 , flipTable[sfrom] , sfrom)]
      
      # -- Move our piece in the piece list
      g_pieceIndex[sto] = g_pieceIndex[sfrom]
      g_pieceList[ ( ((piece & 0xF) << 4) | g_pieceIndex[sto] )] = sto
      
      if ((flags & moveflagPromotion)>0):
        
        newPiece = ( piece & (~0x7) )
        if ( ( flags & moveflagPromoteKnight)>0  ):
          newPiece = ( newPiece | pieceKnight )
        else:
          if ( (flags & moveflagPromoteQueen)>0 ):
            newPiece = ( newPiece | pieceQueen )
          else:
            if ( ( flags & moveflagPromoteBishop)>0 ):
              newPiece = ( newPiece | pieceBishop )
            else:
              newPiece = ( newPiece | pieceRook )
          
        
        g_hashKeyLow = ( g_hashKeyLow ^ g_zobristLow[sto][(piece & 0xF)] )
        g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristHigh[sto][(piece & 0xF)] )
        g_board[sto] = newPiece
        g_hashKeyLow = ( g_hashKeyLow ^ g_zobristLow[sto][(newPiece & 0xF)] )
        g_hashKeyHigh = ( g_hashKeyHigh ^ g_zobristHigh[sto][(newPiece & 0xF)] )
        
        g_baseEval +=  pieceSquareAdj[(newPiece & 0x7)][ iif( sme == 0, flipTable[sto], sto)]

        g_baseEval -=  materialTable[piecePawn]

        g_baseEval +=  materialTable[(newPiece & 0x7)]
        
        pawnType = ( piece & 0xF )
        promoteType = ( newPiece & 0xF )
        
        g_pieceCount[pawnType] -= 1
        
        lastPawnSquare = g_pieceList[ ( (pawnType << 4) | g_pieceCount[pawnType] )]
        g_pieceIndex[lastPawnSquare] = g_pieceIndex[sto]
        g_pieceList[ ((pawnType << 4) | g_pieceIndex[lastPawnSquare])] = lastPawnSquare
        g_pieceList[ ( (pawnType << 4) | g_pieceCount[pawnType] )] = 0
        g_pieceIndex[sto] = g_pieceCount[promoteType]
        g_pieceList[ ( (promoteType << 4) | g_pieceIndex[sto] )] = sto
        g_pieceCount[promoteType] += 1
      else:
        g_board[sto] = g_board[sfrom]

        g_baseEval +=  pieceSquareAdj[(piece & 0x7)][ iif( sme == 0, flipTable[sto], sto)]
        
      g_board[sfrom] = pieceEmpty
      
      g_toMove = otherColor
      g_baseEval = -g_baseEval
      
      if (((piece & 0x7)>0) == ((pieceKing>0) or g_inCheck)):
        if (IsSquareAttackable(g_pieceList[ ( (pieceKing | (8-g_toMove)) << 4)], otherColor)):
          UnmakeMove(move)
          return False
          
      else:
        kingPos = g_pieceList[ ( (pieceKing | (8-g_toMove)) << 4)]
        
        if (ExposesCheck(sfrom, kingPos)):
          UnmakeMove(move)
          return False
          
        
        if (epcEnd != sto):
          if (ExposesCheck(epcEnd, kingPos)):
            UnmakeMove(move)
            return False
        
      g_inCheck = False
      
      if (flags <= moveflagEPC):
        theirKingPos = g_pieceList[ ( (pieceKing | g_toMove) << 4)]
        
        # -- First check if the piece we moved can attack the enemy king
        g_inCheck = IsSquareAttackableFrom(theirKingPos, sto)
        
        if (not g_inCheck):
          # -- Now check if the square we moved from exposes check on the enemy king
          g_inCheck = ExposesCheck(sfrom, theirKingPos)
          
          if (not g_inCheck):
            # -- Finally, ep. capture can cause another square to be exposed
            if (epcEnd != sto):
              g_inCheck = ExposesCheck(epcEnd, theirKingPos)

          
      else:
        # -- Castle or promotion, slow check
        g_inCheck = IsSquareAttackable(g_pieceList[ ( (pieceKing | g_toMove) << 4)], 8-g_toMove)
        
      
      while( len(g_repMoveStack)<g_moveCount ):
        g_repMoveStack.append(0);

      g_repMoveStack[(g_moveCount - 1)] = g_hashKeyLow
      g_move50 = g_move50 + 1
      
      return True
      
    # --
    
    # --
    def UnmakeMove(move):

      global  colorWhite, pieceEmpty, piecePawn, moveflagEPC, moveflagCastleKing
      global  moveflagCastleQueen, moveflagPromotion, g_board, g_toMove
      global  g_castleRights, g_enPassentSquare, g_baseEval
      global  g_hashKeyLow, g_hashKeyHigh, g_inCheck, g_moveCount, g_moveUndoStack
      global  g_move50, g_pieceIndex, g_pieceList, g_pieceCount
      
      g_toMove = 8 - g_toMove
      g_baseEval = -g_baseEval
      
      g_moveCount -= 1
      
      otherColor = 8 - g_toMove
      sme = ( g_toMove >> 3 )
      sthem = ( otherColor >> 3 )
      
      flags = ( move & 0xFF0000 )
      captured = g_moveUndoStack[g_moveCount].captured
      sto = ( (move >> 8) & 0xFF )
      sfrom = ( move & 0xFF )
      
      piece = g_board[sto]
      rook = 0
      rookIndex = 0
      epcEnd = 0
      pawnType = 0
      promoteType = 0
      lastPromoteSquare = 0
      captureType = 0
      
      g_enPassentSquare = g_moveUndoStack[g_moveCount].ep
      g_castleRights = g_moveUndoStack[g_moveCount].castleRights
      g_inCheck = g_moveUndoStack[g_moveCount].inCheck
      g_baseEval = g_moveUndoStack[g_moveCount].baseEval

      g_hashKeyLow = g_moveUndoStack[g_moveCount].hashKeyLow
      g_hashKeyHigh = g_moveUndoStack[g_moveCount].hashKeyHigh
      g_move50 = g_moveUndoStack[g_moveCount].move50
      
      if (flags>0):
        if ( (flags & moveflagCastleKing)>0 ):
          rook = g_board[(sto - 1)]
          g_board[(sto + 1)] = rook
          g_board[(sto - 1)] = pieceEmpty
          
          rookIndex = g_pieceIndex[(sto - 1)]
          g_pieceIndex[(sto + 1)] = rookIndex
          g_pieceList[ ( ((rook & 0xF) << 4) | rookIndex )] = sto + 1
          
        else:
          if ( (flags & moveflagCastleQueen)>0 ):
            rook = g_board[(sto + 1)]
            g_board[(sto - 2)] = rook
            g_board[(sto + 1)] = pieceEmpty
            
            rookIndex = g_pieceIndex[(sto + 1)]
            g_pieceIndex[(sto - 2)] = rookIndex
            g_pieceList[ ( ((rook & 0xF) << 4) | rookIndex )] = sto - 2
        
      
      if ( (flags & moveflagPromotion)>0 ):
        piece = ( (g_board[sto] & (~0x7)) | piecePawn )
        g_board[sfrom] = piece
        
        pawnType = ( g_board[sfrom] & 0xF )
        promoteType = ( g_board[sto] & 0xF )
        
        g_pieceCount[promoteType] = g_pieceCount[promoteType] - 1
        
        lastPromoteSquare = g_pieceList[ ( (promoteType << 4) | g_pieceCount[promoteType] )]
        g_pieceIndex[lastPromoteSquare] = g_pieceIndex[sto]
        g_pieceList[ ( (promoteType << 4) | g_pieceIndex[lastPromoteSquare])] = lastPromoteSquare
        g_pieceList[ ( (promoteType << 4) | g_pieceCount[promoteType] )] = 0
        g_pieceIndex[sto] = g_pieceCount[pawnType]
        g_pieceList[ ( (pawnType << 4) | g_pieceIndex[sto] )] = sto
        g_pieceCount[pawnType] = g_pieceCount[pawnType] + 1
      else:
        g_board[sfrom] = g_board[sto]
        
      
      epcEnd = sto
      if ((flags & moveflagEPC)>0):
        if (g_toMove == colorWhite):
          epcEnd = sto + 0x10
        else:
          epcEnd = sto - 0x10
          
        g_board[sto] = pieceEmpty
        
      
      g_board[epcEnd] = captured
      
      # -- Move our piece in the piece list
      g_pieceIndex[sfrom] = g_pieceIndex[sto]
      g_pieceList[ (  ((piece & 0xF) << 4) | g_pieceIndex[sfrom] )] = sfrom
      
      if (captured>0):
        # -- Restore our piece to the piece list
        captureType = ( captured & 0xF )
        g_pieceIndex[epcEnd] = g_pieceCount[captureType]
        g_pieceList[ ( (captureType << 4) | g_pieceCount[captureType] )] = epcEnd
        g_pieceCount[captureType] = g_pieceCount[captureType] + 1
      
    # --
    
    # --
    def ExposesCheck(sfrom, kingPos):

      global  pieceQueen, g_vectorDelta, g_vectdelta, g_board

      index = kingPos - sfrom + 128
      delta = 0
      pos = 0
      piece = 0
      backwardIndex = 0
      # -- If a queen can't reach it, nobody can!
      if ( (g_vectorDelta[index][0] & (1 << pieceQueen)) != 0):
        delta = g_vectdelta[index]
        pos = kingPos + delta
        while (g_board[pos] == 0):
          pos = pos + delta
          
        
        piece = g_board[pos]
        if ( ( (piece & (g_board[kingPos] ^ 0x18)) & 0x18) == 0):
          return False
          
        
        # -- Now see if the piece can actually attack the king
        backwardIndex = pos - kingPos + 128
        return ( (g_vectorDelta[backwardIndex][ ((piece >> 3) & 1)] & (1 << (piece & 0x7))) != 0 )
        
      return False
      
    # --
    
    # --
    
    def IsSquareOnPieceLine(target, sfrom):

      global  g_vectorDelta, g_vectdelta, g_board

      index = sfrom - target + 128
      piece = g_board[sfrom]
      return ((g_vectorDelta[index][ ( (piece >> 3) & 1)] & (1 << (piece & 0x7))) > 0 )
    
    # --
    
    # --
    def GetMoveSAN(move, validMoves):

      global  piecePawn, moveflagEPC, moveflagCastleKing, moveflagCastleQueen, moveflagPromotion
      global  moveflagPromoteKnight, moveflagPromoteQueen, moveflagPromoteBishop
      global  moveflagPromoteBishop, g_board, g_inCheck, PieceCharList
      
      i = 0
      sfrom = ( move & 0xFF )
      sto = ( (move >> 8) & 0xFF )
      movefrom = 0
      moveTo = 0
      
      if ( (move & moveflagCastleKing)>0):
        return "O-O"
        
      if ( (move & moveflagCastleQueen)>0):
        return "O-O-O"
        
      
      pieceType = ( g_board[sfrom] & 0x7 )
      result = ( PieceCharList[pieceType] ).upper()
      
      dupe = False
      rowDiff = True
      colDiff = True
      posmoves = []
      
      if (len(validMoves) == 0):
        validMoves = GenerateValidMoves()
        
      i = 0
      while(i<len(validMoves)):
        moveFrom = ( validMoves[i] & 0xFF )
        moveTo = ( (validMoves[i] >> 8) & 0xFF )
        if (moveFrom != sfrom and moveTo == sto and ((g_board[moveFrom] & 0x7) == pieceType)):
          dupe = True
          if ((moveFrom & 0xF0) == (sfrom & 0xF0)):
            rowDiff = False
            
          if ((moveFrom & 0x0F) == (sfrom & 0x0F)):
            colDiff = False
        i += 1
 
        
      fmove = FormatSquare(sfrom)

      if (dupe):
        if (colDiff):
          result +=  fmove[0]
        else:
          if (rowDiff):
            result +=  fmove[1]
          else:
            result +=  fmove
          
      else:
        if ((pieceType == piecePawn) and (g_board[sto] != 0)):
          result +=  fmove[0]

      
      if ((g_board[sto] != 0) or ((move & moveflagEPC)>0)):
        result +=  "x"
        
      
      result +=  FormatSquare(sto)
      
      if ( ( move & moveflagPromotion )>0 ):
        if (( move & moveflagPromoteBishop )>0 ):
          result +=  "=B"
        else:
          if ( ( move & moveflagPromoteKnight )>0 ):
            result +=  "=N"
          else:
            if ( ( move & moveflagPromoteQueen )>0 ):
              result +=  "=Q"
            else:
              result +=  "=R"
        
      MakeMove(move)
      
      if (g_inCheck):
        posmoves = GenerateValidMoves()
        result +=  iif(len( posmoves )==0 , "#" , "+" )
        
      UnmakeMove(move)
      
      return result
      
    # --
    
    # --
    def GenerateMove(sfrom, sto):
      return ( sfrom | (sto << 8) )
      
    # --
    
    # --
    def GenerateMove2(sfrom, sto, flags):
      return ( sfrom | ( (sto << 8) | flags ) )
      
    # --
    
    # --
    def GenerateValidMoves():
      moveList = []      #-- new Array()
      allMoves = []      #-- new Array()
      GenerateCaptureMoves(allMoves)
      GenerateAllMoves(allMoves)

      i = len(allMoves)-1
      while(i>=0):

        if (MakeMove(allMoves[i])):
          moveList.append( allMoves[i] )
          UnmakeMove(allMoves[i])
        i -= 1

      return moveList
      
    # --
    
    # --
    def GenerateAllMoves(moveStack):

      global  pieceEmpty, moveflagCastleKing, moveflagCastleQueen, g_board, g_toMove, g_castleRights
      global  g_inCheck, g_pieceList
      
      sfrom = 0
      piece = 0
      pieceIdx = 0
      castleRights = 0
      
      # -- Pawn quiet moves
      pieceIdx = ( (g_toMove | 1) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        GeneratePawnMoves(moveStack, sfrom)
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      # -- Knight quiet moves
      pieceIdx = ( (g_toMove | 2) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        MSt(moveStack, 1, sfrom, 31, None)
        MSt(moveStack, 1, sfrom, 33, None)
        MSt(moveStack, 1, sfrom, 14, None)
        MSt(moveStack, 1, sfrom, -14, None)
        MSt(moveStack, 1, sfrom, -31, None)
        MSt(moveStack, 1, sfrom, -33, None)
        MSt(moveStack, 1, sfrom, 18, None)
        MSt(moveStack, 1, sfrom, -18, None)
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      # -- Bishop quiet moves
      pieceIdx = ( (g_toMove | 3) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        MSt(moveStack, 2, sfrom, -15, None)
        MSt(moveStack, 2, sfrom, -17, None)
        MSt(moveStack, 2, sfrom, 15, None)
        MSt(moveStack, 2, sfrom, 17, None)
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      # -- Rook quiet moves
      pieceIdx = ( (g_toMove | 4) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        MSt(moveStack, 2, sfrom, -1, None)
        MSt(moveStack, 2, sfrom, 1, None)
        MSt(moveStack, 2, sfrom, 16, None)
        MSt(moveStack, 2, sfrom, -16, None)
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      # -- Queen quiet moves
      pieceIdx = ( (g_toMove | 5) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        MSt(moveStack, 2, sfrom, -15, None)
        MSt(moveStack, 2, sfrom, -17, None)
        MSt(moveStack, 2, sfrom, 15, None)
        MSt(moveStack, 2, sfrom, 17, None)
        MSt(moveStack, 2, sfrom, -1, None)
        MSt(moveStack, 2, sfrom, 1, None)
        MSt(moveStack, 2, sfrom, 16, None)
        MSt(moveStack, 2, sfrom, -16, None)
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      # -- King quiet moves
      
      pieceIdx = ( (g_toMove | 6) << 4 )
      sfrom = g_pieceList[pieceIdx]
      MSt(moveStack, 1, sfrom, -15, None)
      MSt(moveStack, 1, sfrom, -17, None)
      MSt(moveStack, 1, sfrom, 15, None)
      MSt(moveStack, 1, sfrom, 17, None)
      MSt(moveStack, 1, sfrom, -1, None)
      MSt(moveStack, 1, sfrom, 1, None)
      MSt(moveStack, 1, sfrom, -16, None)
      MSt(moveStack, 1, sfrom, 16, None)
      
      if (not g_inCheck):
        castleRights = g_castleRights
        if ( g_toMove == 0 ):
          castleRights = ( castleRights >> 2 )
          
        if ( ( castleRights & 1 )>0 ):
          # -- Kingside castle
          if (g_board[(sfrom + 1)] == pieceEmpty and g_board[(sfrom + 2)] == pieceEmpty):
            moveStack.append( GenerateMove2(sfrom, sfrom + 0x02, moveflagCastleKing) )
            
          
        if ( ( castleRights & 2 )>0 ):
          # -- Queenside castle
          if (g_board[(sfrom - 1)] == pieceEmpty and g_board[(sfrom - 2)] == pieceEmpty and g_board[(sfrom - 3)] == pieceEmpty):
            moveStack.append( GenerateMove2(sfrom, sfrom - 0x02, moveflagCastleQueen) )
       
    # --
    
    # --
    def MSt( moveStack, usage, sfrom, dt, enemy ):

      global  g_board

      sto = sfrom + dt
      if( usage == 1 ):
        if((enemy==None and g_board[sto] == 0) or (enemy!=None and (g_board[sto] & enemy)>0)):
          moveStack.append( GenerateMove(sfrom, sto) )
          
      else:
        if( usage == 2 ):
          while (g_board[sto] == 0 ):
            moveStack.append( GenerateMove(sfrom, sto) )
            sto += dt
            
        else:
          if( usage == 3 ):
            
            while (g_board[sto] == 0 ):
              sto += dt
            
            if ((g_board[sto] & enemy)>0):
              moveStack.append( GenerateMove(sfrom, sto) )

    # --
    
    # --
    def GenerateCaptureMoves(moveStack):

      global  colorWhite, piecePawn, moveflagEPC, g_board, g_toMove
      global  g_enPassentSquare, g_pieceList

      sfrom = 0
      sto = 0
      piece = 0
      pieceIdx = 0
      pawn = 0
      inc = iif((g_toMove == 8) , -16 , 16 )
      enemy = iif(g_toMove == 8 , 0x10 , 0x8 )
      
      # -- Pawn captures
      pieceIdx = ( (g_toMove | 1) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        sto = sfrom + inc - 1
        if ( (g_board[sto] & enemy )>0 ):
          MovePawnTo(moveStack, sfrom, sto)
          
        
        sto = sfrom + inc + 1
        if ( ( g_board[sto] & enemy)>0 ):
          MovePawnTo(moveStack, sfrom, sto)
          
        
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      if (g_enPassentSquare != -1):
        inc = iif( (g_toMove == colorWhite), -16 , 16 )
        pawn = ( g_toMove | piecePawn )
        
        sfrom = g_enPassentSquare - (inc + 1)
        if ((g_board[sfrom] & 0xF) == pawn):
          moveStack.append( GenerateMove2(sfrom, g_enPassentSquare, moveflagEPC) )
          
        
        sfrom = g_enPassentSquare - (inc - 1)
        if ((g_board[sfrom] & 0xF) == pawn):
          moveStack.append( GenerateMove2(sfrom, g_enPassentSquare, moveflagEPC) )
          
        
      # -- Knight captures
      pieceIdx = ( (g_toMove | 2) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      
      while (sfrom != 0):
        MSt(moveStack, 1, sfrom, 31, enemy)
        MSt(moveStack, 1, sfrom, 33, enemy)
        MSt(moveStack, 1, sfrom, 14, enemy)
        MSt(moveStack, 1, sfrom, -14, enemy)
        MSt(moveStack, 1, sfrom, -31, enemy)
        MSt(moveStack, 1, sfrom, -33, enemy)
        MSt(moveStack, 1, sfrom, 18, enemy)
        MSt(moveStack, 1, sfrom, -18, enemy)
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      # -- Bishop captures
      pieceIdx = ( (g_toMove | 3) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      
      while (sfrom != 0):
        MSt(moveStack, 3, sfrom, -15, enemy)
        MSt(moveStack, 3, sfrom, -17, enemy)
        MSt(moveStack, 3, sfrom, 15, enemy)
        MSt(moveStack, 3, sfrom, 17, enemy)
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      # -- Rook captures
      pieceIdx = ( (g_toMove | 4) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        MSt(moveStack, 3, sfrom, -1, enemy)
        MSt(moveStack, 3, sfrom, 1, enemy)
        MSt(moveStack, 3, sfrom, -16, enemy)
        MSt(moveStack, 3, sfrom, 16, enemy)
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
      
      
      # -- Queen captures
      pieceIdx = ( (g_toMove | 5) << 4 )
      sfrom = g_pieceList[pieceIdx]
      pieceIdx += 1
      while (sfrom != 0):
        MSt(moveStack, 3, sfrom, -15, enemy)
        MSt(moveStack, 3, sfrom, -17, enemy)
        MSt(moveStack, 3, sfrom, 15, enemy)
        MSt(moveStack, 3, sfrom, 17, enemy)
        MSt(moveStack, 3, sfrom, -1, enemy)
        MSt(moveStack, 3, sfrom, 1, enemy)
        MSt(moveStack, 3, sfrom, -16, enemy)
        MSt(moveStack, 3, sfrom, 16, enemy)
        sfrom = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      # -- King captures
      
      pieceIdx = ( (g_toMove | 6) << 4 )
      sfrom = g_pieceList[pieceIdx]
      MSt(moveStack, 1, sfrom, -15, enemy)
      MSt(moveStack, 1, sfrom, -17, enemy)
      MSt(moveStack, 1, sfrom, 15, enemy)
      MSt(moveStack, 1, sfrom, 17, enemy)
      MSt(moveStack, 1, sfrom, -1, enemy)
      MSt(moveStack, 1, sfrom, 1, enemy)
      MSt(moveStack, 1, sfrom, -16, enemy)
      MSt(moveStack, 1, sfrom, 16, enemy)
      
      
    # --
    
    # --
    def MovePawnTo(moveStack, start, square):

      global  moveflagPromotion, moveflagPromoteKnight, moveflagPromoteQueen, moveflagPromoteBishop

      row = ( square & 0xF0 )
      if ((row == 0x90) or (row == 0x20)):
        moveStack.append( GenerateMove2(start, square, (moveflagPromotion | moveflagPromoteQueen)) )
        moveStack.append( GenerateMove2(start, square, (moveflagPromotion | moveflagPromoteKnight)) )
        moveStack.append( GenerateMove2(start, square, (moveflagPromotion | moveflagPromoteBishop)) )
        moveStack.append( GenerateMove2(start, square, moveflagPromotion) )
        
      else:
        moveStack.append( GenerateMove2(start, square, 0) )
        
      
    # --
    
    # --
    def GeneratePawnMoves(moveStack, sfrom):

      global  colorWhite, pieceEmpty, g_board

      piece = g_board[sfrom]
      color = (piece & colorWhite )
      inc = iif((color == colorWhite) , -16 , 16 )
      sto = sfrom + inc
      # -- Quiet pawn moves

      if (g_board[sto] == 0):
        MovePawnTo(moveStack, sfrom, sto)    # orig.parm. pieceEmpty at the end
        # -- Check if we can do a 2 square jump
        if ((((sfrom & 0xF0) == 0x30) and color != colorWhite) or (((sfrom & 0xF0) == 0x80) and color == colorWhite)):
          sto += inc
          if (g_board[sto] == 0):
            moveStack.append( GenerateMove(sfrom, sto) )

    # --
    
    # --
    def See(move):

      global  colorWhite, piecePawn, pieceKnight, pieceBishop
      global  pieceQueen, pieceKing, g_seeValues, g_board

      sfrom = ( move & 0xFF )
      sto = ( (move >> 8) & 0xFF )
      
      fromPiece = g_board[sfrom]
      sus = iif( (fromPiece & colorWhite)>0 , colorWhite , 0 )
      sthem = 8 - sus
      themAttacks = []      #-- new Array()
      usAttacks = []      #-- new Array()
      
      fromValue = g_seeValues[ (fromPiece & 0xF)]
      toValue = g_seeValues[ (g_board[sto] & 0xF)]
      seeValue = toValue - fromValue
      inc = iif( (fromPiece & colorWhite)>0 , -16 , 16 )
      captureDeficit = fromValue - toValue
      pieceType = 0
      pieceValue = 0
      i = 0
      capturingPieceSquare = 0
      capturingPieceValue = 1000
      capturingPieceIndex = -1
      
      if (fromValue <= toValue):
        return True
        
      if ( (move >> 16)>0 ):
        # -- Castles, promotion, ep are always good
        return True
      
      
      # -- Pawn attacks
      # -- If any opponent pawns can capture back, this capture is probably not worthwhile (as we must be using knight or above).
      # -- Note: this is capture direction from to, so reversed from normal move direction
      if (((g_board[ (sto + inc + 1)] & 0xF) == (piecePawn | sthem)) or ((g_board[ (sto + inc - 1)] & 0xF) == (piecePawn | sthem))):
        return False

      
      # -- Knight attacks
      # -- If any opponent knights can capture back, and the deficit we have to make up is greater than the knights value,
      # -- it's not worth it.  We can capture on this square again, and the opponent doesn't have to capture back.
      
      SeeAddKnightAttacks(sto, sthem, themAttacks)
      if ((len(themAttacks) != 0) and (captureDeficit > g_seeValues[pieceKnight])):
        return False
        
      
      # -- Slider attacks
      g_board[sfrom] = 0
      pieceType = pieceBishop
      while( pieceType <= pieceQueen ):
        if (SeeAddSliderAttacks(sto, sthem, themAttacks, pieceType)):
          if (captureDeficit > g_seeValues[pieceType]):
            g_board[sfrom] = fromPiece
            return False
        pieceType += 1
            
      
      # -- Pawn defenses
      # -- At this point, we are sure we are making a "losing" capture.  The opponent can not capture back with a
      # -- pawn.  They cannot capture back with a minor/major and stand pat either.  So, if we can capture with
      # -- a pawn, it's got to be a winning or equal capture.
      if (((g_board[(sto - inc + 1)] & 0xF) == (piecePawn | sus)) or ((g_board[(sto - inc - 1)] & 0xF) == (piecePawn | sus))):
        g_board[sfrom] = fromPiece
        return True
        
      
      # -- King attacks
      SeeAddSliderAttacks(sto, sthem, themAttacks, pieceKing)
      
      # -- Our attacks
      SeeAddKnightAttacks(sto, sus, usAttacks)
      pieceType = pieceBishop
      while( pieceType <=pieceKing ):
        SeeAddSliderAttacks(sto, sus, usAttacks, pieceType)
        pieceType += 1        
      
      g_board[sfrom] = fromPiece
      
      # -- We are currently winning the amount of material of the captured piece, time to see if the opponent
      # -- can get it back somehow.  We assume the opponent can capture our current piece in this score, which
      # -- simplifies the later code considerably.
      
      while (True):
        capturingPieceValue = 1000
        capturingPieceIndex = -1
        
        # -- Find the least valuable piece of the opponent that can attack the square
        i = 0
        while(i<len(themAttacks)):
          if (themAttacks[i] != 0):
            pieceValue = g_seeValues[ (g_board[themAttacks[i]] & 0x7)]
            if (pieceValue < capturingPieceValue):
              capturingPieceValue = pieceValue
              capturingPieceIndex = i
          i += 1
  
        
        if (capturingPieceIndex == -1):
          # -- Opponent can't capture back, we win
          return True
          
        
        # -- Now, if seeValue < 0, the opponent is winning.  If even after we take their piece,
        # -- we can't bring it back to 0, then we have lost this battle.
        seeValue +=  capturingPieceValue
        if (seeValue < 0):
          return False
          
        
        capturingPieceSquare = themAttacks[capturingPieceIndex]
        themAttacks[capturingPieceIndex] = 0
        
        # -- Add any x-ray attackers
        SeeAddXrayAttack(sto, capturingPieceSquare, sus, usAttacks, themAttacks)
        
        # -- Our turn to capture
        capturingPieceValue = 1000
        capturingPieceIndex = -1
        
        # -- Find our least valuable piece that can attack the square
        i = 0
        while(i<len(usAttacks)):
          if (usAttacks[i] != 0):
            pieceValue = g_seeValues[ ( g_board[usAttacks[i]] & 0x7 )]
            if (pieceValue < capturingPieceValue):
              capturingPieceValue = pieceValue
              capturingPieceIndex = i
          i += 1
          
        
        if (capturingPieceIndex == -1):
          # -- We can't capture back, we lose :(
          return False
          
        
        # -- Assume our opponent can capture us back, and if we are still winning, we can stand-pat
        # -- here, and assume we've won.
        seeValue -=  capturingPieceValue
        if (seeValue >= 0):
          return True
          
        
        capturingPieceSquare = usAttacks[capturingPieceIndex]
        usAttacks[capturingPieceIndex] = 0
        
        # -- Add any x-ray attackers
        SeeAddXrayAttack(sto, capturingPieceSquare, sus, usAttacks, themAttacks)
        
      
    # --
    
    # --
    def SeeAddXrayAttack(target, square, sus, usAttacks, themAttacks):

      global  g_vectorDelta, g_vectdelta, g_board

      index = square - target + 128
      delta = -g_vectdelta[index]
      if (delta == 0):
        return
        
      square += delta
      while (g_board[square] == 0):
        square += delta
        
      
      if (((g_board[square] & 0x18)>0) and IsSquareOnPieceLine(target, square)):
        if ((g_board[square] & 8) == sus):
          usAttacks.append( square )
        else:
          themAttacks.append( square )
       
      
    # --
    
    # -- target = attacking square, sus = color of knights to look for, attacks = array to add squares to
    def SeeAddKnightAttacks(target, sus, attacks):

      global  pieceKnight, g_pieceList

      pieceIdx = ( (sus | pieceKnight) << 4 )
      attackerSq = g_pieceList[pieceIdx]
      pieceIdx += 1
      
      while (attackerSq != 0):
        if (IsSquareOnPieceLine(target, attackerSq)):
          attacks.append( attackerSq )
          
        attackerSq = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
    # --
    
    # --
    def SeeAddSliderAttacks(target, sus, attacks, pieceType):

      global  g_pieceList

      pieceIdx = ( (sus | pieceType) << 4 )
      attackerSq = g_pieceList[pieceIdx]
      
      hit = False
      pieceIdx += 1
      
      while (attackerSq != 0):
        if (IsSquareAttackableFrom(target, attackerSq)):
          attacks.append( attackerSq )
          hit = True
          
        attackerSq = g_pieceList[pieceIdx]
        pieceIdx += 1
        
      
      return hit
      
    # --
    
    # --
    def FormatMove(move):

      global  moveflagPromotion, moveflagPromoteKnight, moveflagPromoteQueen, moveflagPromoteBishop

      result = FormatSquare((move & 0xFF)) + FormatSquare(( (move >> 8) & 0xFF))
      if ((move & moveflagPromotion)>0):
        if ( ( move & moveflagPromoteBishop )>0 ):
          result +=  "b"
        else:
          if ( ( move & moveflagPromoteKnight )>0 ):
            result +=  "n"
          else:
            if ( (move & moveflagPromoteQueen)>0 ):
              result +=  "q"
            else:
              result +=  "r"
              
       
      return result
      
    # --
    
    # --
    def GetMoveFromString(moveString):

      moves = GenerateValidMoves()
      i = 0
      while(i<len(moves)):
        if (FormatMove(moves[i]) == moveString):
          return moves[i]
        i += 1
          
        
      print("busted! ->" + moveString + " fen:" + GetFen())
      
    # --
    
    # --
    def PVFromHash(move, ply):

      global  g_hashKeyLow, g_hashKeyHigh, g_hashMask, g_hashTable

      pvString = ""
      hashNode = 0
      
      if(ply != 0):
        
        pvString = " " + GetMoveSAN(move, [])

        MakeMove(move)
        
        hashNode = g_hashTable[ (g_hashKeyLow & g_hashMask)]
        if ((hashNode != None) and (hashNode.lock == g_hashKeyHigh) and (hashNode.bestMove != None)):
          pvString += PVFromHash(hashNode.bestMove, ply - 1)
          
        
        UnmakeMove(move)
        
      return pvString
      
    # --
    
    # -- To display
    def BuildPVMessage(bestMove, value, ply):

      global  g_nodeCount, g_qNodeCount
      
      totalNodes = g_nodeCount + g_qNodeCount
      return "Ply:" + str(ply) + " Score:" + str(value) + " Nodes:" + str(totalNodes) + " " + PVFromHash(bestMove, 15)
      
    # --
    
    # -- Called on Ply finish
    def finishPlyCallback(bestMove, value, ply):
      if (bestMove != None and bestMove != 0):
        print(BuildPVMessage(bestMove, value, ply))
        
      return
    # --
    
    # -- Called on Move ready to answer
    def finishMoveCallback(bestMove, value, ply):

      global  g_foundmove

      if (bestMove != None and bestMove != 0):

        MakeMove(bestMove)
        print(FormatMove(bestMove))
        
        g_foundmove = bestMove
        
      return
    # --
    
    # -- Produces a chess game   Lua vs Lua
    def autogame():
      
      mv=0
      col=-1
      
      while(True):
        
        col = -col
        if(col>0):
          mv += 1
          print( "Move: " + str(mv) + ". ")
          
        
        Search(4)
        
        if(g_foundmove == 0):
          break
          
    
    # --
    # --
    # -- Here we start
    # --



    InitializeEval()
 
    ResetGame()
  
    InitializeFromFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    autogame()
