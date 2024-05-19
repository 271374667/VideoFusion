import os
from pathlib import Path

from gooey import Gooey, GooeyParser

from src.core.enums import Orientation, Rotation
from src.main import VideoMosaic


@Gooey(program_name="Video Mosaic", program_description='Video Mosaic', use_cmd_args=True)
def main():
    parser = GooeyParser(description='Video Mosaic')
    parser.add_argument('input', type=str, help='Input directory or txt file')
    parser.add_argument('--output_file_path', type=str, default='output.mp4', help='Output file path')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second')
    parser.add_argument('--sample_rate', type=float, default=0.5, help='Sample rate')
    parser.add_argument('--video_orientation', type=str, choices=[e.name for e in Orientation],
                        default=Orientation.VERTICAL.name, help='Video orientation')
    parser.add_argument('--horizontal_rotation', type=str, choices=[e.name for e in Rotation],
                        default=Rotation.CLOCKWISE.name,
                        help='Horizontal rotation')
    parser.add_argument('--vertical_rotation', type=str, choices=[e.name for e in Rotation],
                        default=Rotation.CLOCKWISE.name,
                        help='Vertical rotation')

    args = parser.parse_args()

    vm = VideoMosaic()
    vm.output_file_path = args.output_file_path
    vm.fps = args.fps
    vm.sample_rate = args.sample_rate
    vm.video_orientation = Orientation[args.video_orientation]
    vm.horizontal_rotation = Rotation[args.horizontal_rotation]
    vm.vertical_rotation = Rotation[args.vertical_rotation]

    if os.path.isdir(args.input):
        vm.add_video_dir(args.input)
    elif os.path.isfile(args.input) and Path(args.input).suffix == '.txt':
        vm.read_from_txt_file(args.input)
    else:
        raise ValueError('Invalid input. Please provide a directory or a txt file.')
    vm.start()


if __name__ == '__main__':
    main()
