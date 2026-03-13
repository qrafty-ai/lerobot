#!/usr/bin/env python

import torch

from lerobot.policies.xvla.action_hub import build_action_space


def test_chunk_delta_joint_roundtrip_default_layout():
    action_space = build_action_space(
        "chunk_delta_joint",
        real_dim=14,
        max_dim=20,
        gripper_indices=[6, 13],
    )

    proprio = torch.tensor(
        [
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 0.2, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 0.8],
            [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.4, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 0.6],
        ]
    )
    action = torch.tensor(
        [
            [
                [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 1.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 0.0],
                [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 0.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 1.0],
            ],
            [
                [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 1.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 0.0],
                [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 0.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 1.0],
            ],
        ]
    )

    encoded = action_space.encode_targets(action, proprio)
    decoded = action_space.decode_actions(encoded, proprio)

    assert encoded.shape[-1] == 20
    assert decoded.shape[-1] == 20
    torch.testing.assert_close(decoded[..., :14], action, rtol=0, atol=0)
    torch.testing.assert_close(decoded[..., 14:], torch.zeros_like(decoded[..., 14:]), rtol=0, atol=0)


def test_chunk_delta_joint_roundtrip_padded_layout():
    action_space = build_action_space(
        "chunk_delta_joint",
        real_dim=18,
        max_dim=20,
        gripper_indices=[16, 17],
        action_joint_indices=list(range(16)),
        state_joint_indices=list(range(16)),
    )

    proprio = torch.tensor(
        [
            [
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
                13.0,
                14.0,
                15.0,
                16.0,
                0.25,
                0.75,
                101.0,
                102.0,
                103.0,
                104.0,
                105.0,
                106.0,
                107.0,
                108.0,
                109.0,
                110.0,
                111.0,
                112.0,
                113.0,
                114.0,
                115.0,
                116.0,
                117.0,
                118.0,
                119.0,
                120.0,
                121.0,
                122.0,
                123.0,
                124.0,
                125.0,
                126.0,
                127.0,
                128.0,
                129.0,
                130.0,
                131.0,
                132.0,
                133.0,
                134.0,
            ]
        ]
    )
    action = torch.tensor(
        [
            [
                [
                    2.0,
                    3.0,
                    4.0,
                    5.0,
                    6.0,
                    7.0,
                    8.0,
                    9.0,
                    10.0,
                    11.0,
                    12.0,
                    13.0,
                    14.0,
                    15.0,
                    16.0,
                    17.0,
                    1.0,
                    0.0,
                ],
                [
                    3.0,
                    4.0,
                    5.0,
                    6.0,
                    7.0,
                    8.0,
                    9.0,
                    10.0,
                    11.0,
                    12.0,
                    13.0,
                    14.0,
                    15.0,
                    16.0,
                    17.0,
                    18.0,
                    0.0,
                    1.0,
                ],
            ]
        ]
    )

    encoded = action_space.encode_targets(action, proprio)
    decoded = action_space.decode_actions(encoded, proprio)

    assert encoded.shape[-1] == 20
    assert decoded.shape[-1] == 20
    torch.testing.assert_close(decoded[..., :18], action, rtol=0, atol=0)
    torch.testing.assert_close(decoded[..., 18:], torch.zeros_like(decoded[..., 18:]), rtol=0, atol=0)


def test_chunk_delta_joint_postprocess_clamps_grippers():
    action_space = build_action_space(
        "chunk_delta_joint",
        real_dim=18,
        max_dim=20,
        gripper_indices=[16, 17],
        action_joint_indices=list(range(16)),
        state_joint_indices=list(range(16)),
    )

    raw_action = torch.tensor(
        [
            [
                [
                    0.0,
                    1.0,
                    2.0,
                    3.0,
                    4.0,
                    5.0,
                    6.0,
                    7.0,
                    8.0,
                    9.0,
                    10.0,
                    11.0,
                    12.0,
                    13.0,
                    14.0,
                    15.0,
                    -3.0,
                    4.0,
                    99.0,
                    100.0,
                ]
            ]
        ]
    )

    processed = action_space.postprocess(raw_action)

    assert processed.shape[-1] == 18
    torch.testing.assert_close(processed[..., :16], raw_action[..., :16], rtol=0, atol=0)
    torch.testing.assert_close(processed[..., 16], torch.zeros_like(processed[..., 16]), rtol=0, atol=0)
    torch.testing.assert_close(processed[..., 17], torch.ones_like(processed[..., 17]), rtol=0, atol=0)
