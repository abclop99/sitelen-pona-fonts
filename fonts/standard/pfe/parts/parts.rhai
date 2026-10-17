// Shared parts, imported from the earlier Inkscape drawings.

// Part arrowhead, drawn on page part-arrowhead.
fn arrowhead() {
    let out = [];
    out.push(path(pt(672.76, 311.03)).line(pt(790.071, 458.656)).line(pt(649.034, 598.374)));
    out
}

// Part big-box, drawn on page part-big-box.
fn big_box() {
    let out = [];
    out.push(path(pt(136.55, 770.441))
            .line(pt(136.55, 29.559))
            .line(pt(763.45, 29.559))
            .line(pt(763.45, 770.441)));
    out
}

// Part big-circle, drawn on page part-big-circle.
fn big_circle() {
    let out = [];
    out.push(path(pt(75.001, 399.998))
            .controls(pt(75.001, 192.891), pt(242.895, 24.997), pt(450.002, 24.997))
            .controls(pt(657.109, 24.997), pt(825.003, 192.891), pt(825.003, 399.998))
            .controls(pt(825.003, 607.105), pt(657.109, 774.999), pt(450.002, 774.999))
            .controls(pt(242.895, 774.999), pt(75.001, 607.105), pt(75.001, 399.998))
            .close());
    out
}

// Part big-dot, drawn on page part-big-dot.
fn big_dot() {
    let out = [];
    out.push(path(pt(420, 400))
            .controls(pt(420, 383.4), pt(433.4, 370), pt(450, 370))
            .controls(pt(466.6, 370), pt(480, 383.4), pt(480, 400))
            .controls(pt(480, 416.6), pt(466.6, 430), pt(450, 430))
            .controls(pt(433.4, 430), pt(420, 416.6), pt(420, 400))
            .close());
    out.push(path(pt(450, 400)).line(pt(450.1, 400)));
    out
}

// Part big-triangle, drawn on page part-big-triangle.
fn big_triangle() {
    let out = [];
    out.push(path(pt(450, 774.999))
            .line(pt(809.998, 25.003))
            .line(pt(90.003, 25.003))
            .line(pt(450, 774.999))
            .close());
    out
}

// Part closed-mouth, drawn on page part-closed-mouth.
fn closed_mouth() {
    let out = [];
    out.push(path(pt(75.005, 566.664))
            .controls(pt(200.004, 108.336), pt(699.999, 108.336), pt(824.997, 566.664)));
    out
}

// Part dot, drawn on page part-dot.
fn dot() {
    let out = [];
    out.push(path(pt(442, 400))
            .controls(pt(442, 395.6), pt(445.6, 392), pt(450, 392))
            .controls(pt(454.4, 392), pt(458, 395.6), pt(458, 400))
            .controls(pt(458, 404.4), pt(454.4, 408), pt(450, 408))
            .controls(pt(445.6, 408), pt(442, 404.4), pt(442, 400))
            .close());
    out.push(path(pt(450, 400)).line(pt(450.1, 400)));
    out
}

// Part hammer, drawn on page part-hammer.
fn hammer() {
    let out = [];
    out.push(path(pt(260, 775))
            .line(pt(640, 775))
            .line(pt(640, 565))
            .line(pt(260, 565))
            .line(pt(260, 775))
            .close());
    out.push(path(pt(450, 775)).line(pt(450, 401.5)));
    out
}

// Part hand, drawn on page part-hand.
fn hand() {
    let out = [];
    out += place(luka(), tf(0.594, 0, 0, 0.493, 141.556, 12.678));
    out
}

// Part head, drawn on page part-head.
fn head() {
    let out = [];
    out.push(path(pt(190.386, 284.613))
            .controls(pt(190.386, 141.191), pt(306.578, 24.998), pt(450.001, 24.998))
            .controls(pt(593.424, 24.998), pt(709.616, 141.191), pt(709.616, 284.613))
            .controls(pt(709.616, 428.036), pt(593.424, 544.229), pt(450.001, 544.229))
            .controls(pt(306.578, 544.229), pt(190.386, 428.036), pt(190.386, 284.613))
            .close());
    out
}

// Part heart, drawn on page part-heart.
fn heart() {
    let out = [];
    out.push(path(pt(450, 605.954))
            .controls(pt(322.895, 861.546), pt(75, 814.474), pt(75, 550.888))
            .controls(pt(75, 363.684), pt(326.645, 202.632), pt(450, 25)));
    out.push(path(pt(450, 605.954))
            .controls(pt(577.105, 861.546), pt(825, 814.474), pt(825, 550.888))
            .controls(pt(825, 363.684), pt(573.355, 202.632), pt(450, 25)));
    out
}

// Part legs, drawn on page part-legs.
fn legs() {
    let out = [];
    out.push(path(pt(75, 83.2))
            .line(pt(271.9, 83.2))
            .line(pt(478.2, 731.3))
            .line(pt(825, 129.9))
            .line(pt(643.7, 68.7)));
    out
}

// Part luka, drawn on page part-luka.
fn luka() {
    let out = [];
    out.push(path(pt(79.934, 301.316))
            .line(pt(262.501, 25.005))
            .controls(pt(262.501, 25.005), pt(247.699, 255.268), pt(262.501, 426.318))
            .controls(pt(277.303, 597.368), pt(386.224, 774.015), pt(512.5, 775.001))
            .controls(pt(638.775, 775.987), pt(746.053, 597.368), pt(762.498, 426.318))
            .controls(pt(778.944, 255.268), pt(762.498, 25.005), pt(762.498, 25.005)));
    out
}

// Part mouth, drawn on page part-mouth.
fn mouth() {
    let out = [];
    out.push(path(pt(294.712, 720.262))
            .line(pt(605.285, 720.262))
            .controls(pt(598.026, 622.039), pt(561.962, 537.802), pt(449.999, 537.802))
            .controls(pt(338.036, 537.802), pt(301.974, 622.039), pt(294.712, 720.262))
            .close());
    out
}

// Part page, drawn on page part-page.
fn page() {
    let out = [];
    out.push(path(pt(136.548, 770.442))
            .line(pt(763.448, 770.442))
            .line(pt(763.448, 29.561))
            .line(pt(136.548, 29.561))
            .line(pt(136.548, 770.442))
            .close());
    out
}

// Part palisa, drawn on page part-palisa.
fn palisa() {
    let out = [];
    out.push(path(pt(363.461, 400))
            .controls(pt(363.461, 192.886), pt(394.615, 25.001), pt(450, 25.001))
            .controls(pt(505.385, 25.001), pt(536.538, 192.886), pt(536.538, 400))
            .controls(pt(536.538, 607.115), pt(505.385, 775), pt(450, 775))
            .controls(pt(394.615, 775), pt(363.461, 607.115), pt(363.461, 400))
            .close());
    out
}

// Part person-head, drawn on page part-person-head.
fn person_head() {
    let out = [];
    out.push(path(pt(144.446, 469.446))
            .controls(pt(144.446, 300.693), pt(281.247, 163.892), pt(450, 163.892))
            .controls(pt(618.753, 163.892), pt(755.554, 300.693), pt(755.554, 469.446))
            .controls(pt(755.554, 638.199), pt(618.753, 775), pt(450, 775))
            .controls(pt(281.247, 775), pt(144.446, 638.199), pt(144.446, 469.446))
            .close());
    out
}

// Part pointer, drawn on page part-pointer.
fn pointer() {
    let out = [];
    out.push(path(pt(481.221, 25))
            .controls(pt(481.221, 25), pt(325.004, 301.316), pt(325.004, 618.746))
            .controls(pt(325.004, 693.287), pt(377.685, 757.44), pt(450.788, 771.965))
            .controls(pt(523.89, 786.491), pt(597.059, 747.341), pt(625.573, 678.471))
            .controls(pt(654.087, 609.602), pt(630.007, 530.188), pt(568.033, 488.787))
            .controls(pt(506.059, 447.386), pt(423.456, 455.533), pt(370.754, 508.248)));
    out
}

// Part rays, drawn on page part-rays.
fn rays() {
    let out = [];
    out.push(path(pt(168.464, 704.505)).line(pt(278.593, 560.982)));
    out.push(path(pt(450.132, 775)).line(pt(450.132, 601.721)));
    out.push(path(pt(731.536, 704.505)).line(pt(621.407, 560.982)));
    out
}

// Part shaft, drawn on page part-shaft.
fn shaft() {
    let out = [];
    out.push(path(pt(450, 775)).line(pt(450, 25.127)));
    out
}

// Part short-box, drawn on page part-short-box.
fn short_box() {
    let out = [];
    out.push(path(pt(136.55, 542.476))
            .line(pt(136.55, 286.018))
            .line(pt(763.45, 286.018))
            .line(pt(763.45, 542.476)));
    out
}

// Part side-box, drawn on page part-side-box.
fn side_box() {
    let out = [];
    out.push(path(pt(193.54, 770.441))
            .line(pt(364.514, 770.441))
            .line(pt(364.514, 29.559))
            .line(pt(193.54, 29.559)));
    out
}

// Part sin, drawn on page part-sin.
fn sin() {
    let out = [];
    out.push(path(pt(450, 638.636)).line(pt(450, 400)));
    out.push(path(pt(75, 229.546)).line(pt(347.728, 229.546)));
    out.push(path(pt(552.272, 229.546)).line(pt(825, 229.546)));
    out
}

// Part small-circle, drawn on page part-small-circle.
fn small_circle() {
    let out = [];
    out.push(path(pt(220, 400))
            .controls(pt(220, 273), pt(323, 170), pt(450, 170))
            .controls(pt(577, 170), pt(680, 273), pt(680, 400))
            .controls(pt(680, 527), pt(577, 630), pt(450, 630))
            .controls(pt(323, 630), pt(220, 527), pt(220, 400))
            .close());
    out
}

// Part small-triangle, drawn on page part-small-triangle.
fn small_triangle() {
    let out = [];
    out.push(path(pt(450, 375.4)).line(pt(227, 25)).line(pt(673, 25)).line(pt(450, 375.4)).close());
    out
}

// Part stem, drawn on page part-stem.
fn stem() {
    let out = [];
    out.push(path(pt(449.641, 775)).line(pt(449.641, 410)));
    out
}

// Part sun, drawn on page part-sun.
fn sun() {
    let out = [];
    out += place(small_circle(), tf(1, 0, 0, 1, 0, 0));
    out += place(sun_rays(), tf(1, 0, 0, 1, 0, 0));
    out
}

// Part sun-rays, drawn on page part-sun-rays.
fn sun_rays() {
    let out = [];
    out.push(path(pt(450, 775)).line(pt(450, 630)));
    out.push(path(pt(450, 170)).line(pt(450, 25)));
    out.push(path(pt(75, 400)).line(pt(220, 400)));
    out.push(path(pt(680, 400)).line(pt(825, 400)));
    out
}

// Part tally, drawn on page part-tally.
fn tally() {
    let out = [];
    out.push(path(pt(450.002, 774.999)).line(pt(450.002, 24.997)));
    out
}

// Part toki-pona, drawn on page part-toki-pona.
fn toki_pona() {
    let out = [];
    out += place(rays(), tf(0.674, 0, 0, 0.674, 146.738, 252.716));
    out += place(head(), tf(1, 0, 0, 1, 0, 0));
    out += place(closed_mouth(), tf(0.292, 0, 0, 0.292, 318.454, 143.248));
    out
}

// Part wave, drawn on page part-wave.
fn wave() {
    let out = [];
    out.push(path(pt(75.003, 439.474))
            .controls(pt(153.947, 301.316), pt(316.072, 319.643), pt(450, 400))
            .controls(pt(583.928, 480.357), pt(746.053, 498.684), pt(825, 360.526)));
    out
}
