// Step 1: Go to the website and click the Go Shopping button
step('Go to the website', async () => {

    await page.goto('http://' + params.my_ip + ':8080/');
    await page.locator('text=Go Shopping').click();
    expect(page.url()).toBe('http://' + params.my_ip + ':8080/#hot-products');

});

// Step 2: Calculate the total amount of products and select a random product
step('Select product', async () => {

    await page.locator('.sc-8119fd44-1').first().waitFor();
    const productCount = await page.locator('.sc-8119fd44-1').count();
    const randomProduct = Math.floor(Math.random() * productCount);
    await page.locator('.sc-8119fd44-1 >> nth=' + randomProduct).click();

});

// Step 3: Add the selected product to the cart
step('Add product to cart', async () => {

    await Promise.all([
        page.waitForNavigation(),
        page.locator('text=Add To Cart').click()

    ]);

});

// Step 4: Place order and make sure it succeeded
step('Place order', async () => {
    await Promise.all([
        page.waitForNavigation(),
        page.locator('text=Place Order').click()

    ]);

    await page.locator('text=Done').click();
    expect(await page.isVisible('text=Done')).toBeTruthy();

});
