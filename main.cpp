#include <iostream>
#include <unordered_set>
#include <string>
#include <uchar.h>
#include <vector>

//An expression should consume the stream until it finds that it is a concluded valid expression or the stream ends
//An expression is a description in the form {one of(x, y), x, y} where x and y are themselves expressions

//In this way, a language is a set of expressions, and validation is performed by recursive descent through one or more expressions
//All validation operations eventually reach the base case, where the subject is compared to a list of valid characters
//A more complex expression performs recursive validation calls until it either validates successfully or determines that the input is not compliant with the given expression

//All expression types inherit from this base. This declares a universal validation method which enables type-agnostic recursion
//In other words, the Phrase 'variable' does not need to remember the individual types 'letter' and 'digit | letter', it is only aware of Expression 0 and Expression 1, and simply instructs these to validate themselves

struct Expression {
    public:
        //This is the lynch pin, so to speak
        //Behaviour is defined as follows:
            //If the input is valid, return true and increment index by n, where n is the length of the input
            //If the input is not valid, return false and DO NOT increment index
        virtual bool validate(std::vector<char32_t>& input, int* index) = 0;
};

//A Charset expression is ONE CHARACTER from a predefined set
struct Charset : public Expression {
    private:
        //Because we only need lookup, not iteration, an unordered_set is fastest here
            //An unordered_set is O(1) on average, and O(n) in the worst case. If the character is not present, O(1)
            //Iterating a flat array for lookup is O(n) in the worst case. If the character is not present, O(n)
        std::unordered_set<char32_t> characters;

    public:
        Charset(std::initializer_list<char32_t> _characters) : characters(_characters) {}

        bool validate(std::vector<char32_t>& input, int* index) override {
            char32_t& c = input[*index];
            if(characters.contains(c)) {
                (*index)++;
                return true;
            } else return false;
        }
};

//A Mutable expression is ONE OF its child expressions
struct Mutable : public Expression {
    private:
        int count = 0;
        Expression** options = nullptr;
    
    public:
        Mutable(std::initializer_list<Expression*> _options) : count(_options.size()) {
            options = new Expression*[count];
            for(int i = 0; i < count; i++) {
                options[i] = _options.begin()[i];
            }
        }

        bool validate(std::vector<char32_t>& input, int* index) override {
            //We make the assumption that all child expressions of a Mutable expression are mutually exclusive. A language defined otherwise is considered UB
            for(int i = 0; i < count; i++) { 
                if(options[i]->validate(input, index)) return true; 
            }
            return false;
        }
};

//A Sequence expression is ZERO OR MORE OF its child expression
struct Sequence : public Expression {
    private:
        Expression* expression = nullptr;

        //A sequence may be bounded explicity (by an expression) or implicitly (it simply starts/ends when another expression begins). Sequences which are explicitly bounded must be thusly validated
        Expression* initialiser = nullptr;
        Expression* terminator = nullptr;
    
    public:
        Sequence(Expression* _expression, Expression* _initialiser = nullptr, Expression* _terminator = nullptr) : expression(_expression), initialiser(_initialiser), terminator(_terminator) {}

        bool validate(std::vector<char32_t>& input, int* index) override {
            int offset = *index;

            if(initialiser && !initialiser->validate(input, &offset)) return false;
            //If an implicitly bound sequence begins with an invalid character, that simply means it is a length 0 sequence
            else if(!expression->validate(input, &offset)) return true;

            //offset is stepped forward by validate
            for(; offset < input.size();) {
                //We continue to evaluate the stream according to expression until it is invalid
                if(!expression->validate(input, &offset)) break;
            }

            //We evaluate relative to expression until failure. THEN we check for terminator character, if the expression is explicitly bound
            //Note that offset is the index UPON WHICH expression failed to validate
            //This also assumes that expression is mutually exclusive with terminator
            if(terminator && !terminator->validate(input, &offset)) return false;
            else {
                *index = offset;
                return true;
            }
        }
};

//A Phrase expression is an ORDERED SET of child expressions
struct Phrase : public Expression {
    private:
        int count = 0;
        Expression** ordered_list = nullptr;

    public:
        Phrase(std::initializer_list<Expression*> _ordered_list) : count(_ordered_list.size()) {
            ordered_list = new Expression*[count];
            for(int i = 0; i < count; i++) {
                ordered_list[i] = _ordered_list.begin()[i];
            }
        }

        bool validate(std::vector<char32_t>& input, int* index) override {
            for(int i = 0; i < count; i++) {
                if(!ordered_list[i]->validate(input, index)) return false;
            }

            return true;
        }
};

struct Proto_Language_TOCSASS1 {
    Mutable general_expression = Mutable({});

    Charset digit = Charset({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'});
    Sequence numeral = Sequence({&digit});

    Charset letter = Charset({'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'});
    Charset variable_null = Charset({'-'});
    Mutable variable_value = Mutable({&letter, &digit, &variable_null});
    Phrase variable = Phrase({&letter, &variable_value});

    Charset glyph = Charset({U'+', U'×', U'∸', U'⊤', U'⊥', U'←', U'↑', U'→', U'↓', U'∷', U'Θ'});
    
    Charset whitespace = Charset({' '});
    Sequence whitespace_sequence = Sequence({&whitespace});
    Charset lambda = Charset({U'λ'});
    Charset bullet = Charset({'.'});
    Phrase abstraction = Phrase({&lambda, &whitespace_sequence, &variable, &whitespace_sequence, &bullet, &whitespace_sequence, &general_expression});

    Charset brace_open = Charset({'('});
    Charset brace_close = Charset({')'});
    Phrase application = Phrase({&brace_open, &whitespace_sequence, &general_expression, &whitespace, &whitespace_sequence, &general_expression, &whitespace_sequence, &brace_close});

    Proto_Language_TOCSASS1() {
        general_expression = Mutable({&numeral, &variable, &glyph, &abstraction, &application});
    }

    bool validate(std::vector<char32_t>& input) {
        int index = 0;
        return general_expression.validate(input, &index);
    }
};

int translate_utf8(std::string* input, std::vector<char32_t>& output_) {
    for(int i = 0; i < input->length();) {
        unsigned char byte = static_cast<unsigned char>((*input)[i]);
        int length = 0;
        for(; length < 4; length++) {
            if(((byte >> (7 - length)) & 1) == 0) break;
        }

        if(length == 0) length = 1; //ASCII

        char32_t& character = output_.emplace_back();
        switch(length) {
            case 1:
                character = byte;
            break;
            case 2:
                character = ((byte & 0x1F) << 6) | 
                (static_cast<unsigned char>(input->at(i + 1)) & 0x3F);
            break;
            case 3:
                character = ((byte & 0x0F) << 12) | 
                ((static_cast<unsigned char>(input->at(i + 1)) & 0x3F) << 6)|
                (static_cast<unsigned char>(input->at(i + 2)) & 0x3F);
            break;
            case 4:
                character = ((byte & 0x07) << 18) | 
                ((static_cast<unsigned char>(input->at(i + 1)) & 0x3F) << 12)|
                ((static_cast<unsigned char>(input->at(i + 2)) & 0x3F) << 6)|
                (static_cast<unsigned char>(input->at(i + 3)) & 0x3F);
            break;
            default:
                std::cout << "FUCK FUCK SHIT FUCK" << std::endl;
            break;
        }

        i += length;
    }

    return 0;
}

int main() {
    Proto_Language_TOCSASS1 language;

    std::cout << "Type or paste some characters, then press enter: ";

    std::string input;
    std::getline(std::cin, input);

    std::vector<char32_t> encoded;
    translate_utf8(&input, encoded);

    if(language.validate(encoded)) {
        std::cout << "0" << std::endl;
        return 0;
    } else {
        std::cout << "1" << std::endl;
        return 1;
    }
}