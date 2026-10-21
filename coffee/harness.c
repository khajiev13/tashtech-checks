// This harness calls the submitted functions; it contains no solution functions.
#define main submitted_main
#include "coffee_machine.c"
#undef main
#include <string.h>

static int check_stock(Stock got, Stock want)
{
    if (got.water_ml != want.water_ml || got.milk_ml != want.milk_ml ||
        got.beans_g != want.beans_g || got.paper_cups != want.paper_cups)
    {
        fprintf(stderr, "Expected water/milk/beans/cups %i/%i/%i/%i; got %i/%i/%i/%i.\n",
                want.water_ml, want.milk_ml, want.beans_g, want.paper_cups,
                got.water_ml, got.milk_ml, got.beans_g, got.paper_cups);
        return 1;
    }
    return 0;
}

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        return 2;
    }
    if (strcmp(argv[1], "read") == 0)
    {
        int result = read_coffee_choice();
        printf("CHECK50_RETURN=%i\n", result);
        return 0;
    }
    if (strcmp(argv[1], "ids") == 0)
    {
        for (int i = 0; i < COFFEE_COUNT; i++)
        {
            printf("CHECK50_ID=%i\n", coffees[i].id);
        }
        return 0;
    }
    const Coffee latte = {2, "Latte", "Coffee with milk.", 100, 50, 10, 1};
    const Coffee espresso = {1, "Espresso", "Strong coffee without milk.", 100, 0, 10, 1};
    // Different small quantities check that functions use their Coffee argument.
    const Coffee sample = {7, "Sample", "Test recipe.", 80, 30, 12, 2};
    if (strcmp(argv[1], "exact") == 0 || strcmp(argv[1], "no_milk") == 0)
    {
        bool no_milk = strcmp(argv[1], "no_milk") == 0;
        Stock stock = no_milk ? (Stock) {100, 0, 10, 1} : (Stock) {100, 50, 10, 1};
        Coffee coffee = no_milk ? espresso : latte;
        if (!can_make_coffee(stock, coffee))
        {
            fprintf(stderr, "Expected can_make_coffee to return true for exactly the recipe amounts.\n");
            return 1;
        }
        if (!no_milk && !can_make_coffee((Stock) {80, 30, 12, 2}, sample))
        {
            fprintf(stderr, "Expected true for exactly 80/30/12/2 when the recipe needs 80/30/12/2.\n");
            return 1;
        }
        return 0;
    }
    const Stock short_stocks[] = {{99, 50, 10, 1}, {100, 49, 10, 1},
                                  {100, 50, 9, 1}, {100, 50, 10, 0}};
    const Stock short_sample[] = {{79, 30, 12, 2}, {80, 29, 12, 2},
                                  {80, 30, 11, 2}, {80, 30, 12, 1}};
    const char *names[] = {"water", "milk", "beans", "cups"};
    for (int i = 0; i < 4; i++)
    {
        if (strcmp(argv[1], names[i]) == 0)
        {
            if (can_make_coffee(short_stocks[i], latte))
            {
                fprintf(stderr, "Expected false when only %s is below the recipe amount.\n", names[i]);
                return 1;
            }
            if (can_make_coffee(short_sample[i], sample))
            {
                fprintf(stderr, "Expected false when only %s is below the sample recipe's amount.\n", names[i]);
                return 1;
            }
            return 0;
        }
    }
    if (strcmp(argv[1], "deduct") == 0)
    {
        Stock full = {500, 200, 40, 3};
        if (check_stock(stock_after_coffee(full, latte), (Stock) {400, 150, 30, 2}))
        {
            return 1;
        }
        if (check_stock(stock_after_coffee(full, espresso), (Stock) {400, 200, 30, 2}))
        {
            return 1;
        }
        if (check_stock(stock_after_coffee((Stock) {100, 50, 10, 1}, latte), (Stock) {0, 0, 0, 0}))
        {
            return 1;
        }
        return check_stock(stock_after_coffee((Stock) {120, 60, 15, 3}, sample), (Stock) {40, 30, 3, 1});
    }
    if (strcmp(argv[1], "refusal") == 0)
    {
        for (int i = 0; i < 4; i++)
        {
            if (check_stock(stock_after_coffee(short_stocks[i], latte), short_stocks[i]))
            {
                return 1;
            }
        }
        return 0;
    }
    if (strcmp(argv[1], "copy") == 0)
    {
        Stock original = {500, 200, 40, 3};
        can_make_coffee(original, latte);
        if (check_stock(original, (Stock) {500, 200, 40, 3}))
        {
            return 1;
        }
        stock_after_coffee(original, latte);
        if (check_stock(original, (Stock) {500, 200, 40, 3}))
        {
            return 1;
        }
        Stock updated = stock_after_coffee(original, latte);
        if (check_stock(updated, (Stock) {400, 150, 30, 2}))
        {
            return 1;
        }
        return check_stock(original, (Stock) {500, 200, 40, 3});
    }
    return 2;
}
