import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';
import '../models/pet.dart';
import '../theme.dart';

class PetsScreen extends StatelessWidget {
  const PetsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Thú cưng'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: () => _showAddPetDialog(context),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: state.refresh,
        child: state.pets.isEmpty
            ? ListView(children: [
                const SizedBox(height: 120),
                Center(
                  child: Column(
                    children: [
                      Icon(Icons.pets, size: 64, color: AppColors.fgMuted),
                      const SizedBox(height: 12),
                      const Text('Chưa có thú cưng nào',
                          style: TextStyle(fontSize: 16, color: AppColors.fgSecondary)),
                      const SizedBox(height: 16),
                      FilledButton.icon(
                        onPressed: () => _showAddPetDialog(context),
                        icon: const Icon(Icons.add),
                        label: const Text('Thêm thú cưng'),
                      ),
                    ],
                  ),
                ),
              ])
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: state.pets.length,
                itemBuilder: (ctx, i) => _PetCard(pet: state.pets[i]),
              ),
      ),
    );
  }

  void _showAddPetDialog(BuildContext context) {
    final nameCtrl = TextEditingController();
    final breedCtrl = TextEditingController();
    final colorCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Thêm thú cưng'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Tên *'),
              autofocus: true,
            ),
            const SizedBox(height: 10),
            TextField(
              controller: breedCtrl,
              decoration: const InputDecoration(labelText: 'Giống'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: colorCtrl,
              decoration: const InputDecoration(labelText: 'Màu lông'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () async {
              final name = nameCtrl.text.trim();
              if (name.isEmpty) return;
              Navigator.pop(ctx);
              await context.read<AppState>().addPet(
                    name,
                    breed: breedCtrl.text.trim(),
                    color: colorCtrl.text.trim(),
                  );
            },
            child: const Text('Thêm'),
          ),
        ],
      ),
    );
  }
}

class _PetCard extends StatelessWidget {
  final Pet pet;
  const _PetCard({required this.pet});

  @override
  Widget build(BuildContext context) {
    final statusColor = pet.isReady ? AppColors.green : AppColors.orange;
    final statusText = pet.isReady ? 'Sẵn sàng' : '${pet.embeddingCount}/5 ảnh';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            CircleAvatar(
              radius: 28,
              backgroundColor: AppColors.greenLight,
              child: Text(
                pet.name.isNotEmpty ? pet.name[0].toUpperCase() : '?',
                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700, color: AppColors.green),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(pet.name,
                      style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 2),
                  Text(
                    [if (pet.breed.isNotEmpty) pet.breed, if (pet.color.isNotEmpty) pet.color]
                        .join(' - '),
                    style: const TextStyle(fontSize: 13, color: AppColors.fgSecondary),
                  ),
                  if (pet.lastSeenAt != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        'Lần cuối: ${_fmtAgo(pet.lastSeenAt!)}',
                        style: const TextStyle(fontSize: 12, color: AppColors.fgMuted),
                      ),
                    ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: statusColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(statusText,
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: statusColor)),
            ),
          ],
        ),
      ),
    );
  }

  String _fmtAgo(DateTime dt) {
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 1) return 'Vừa xong';
    if (diff.inMinutes < 60) return '${diff.inMinutes} phút trước';
    if (diff.inHours < 24) return '${diff.inHours} giờ trước';
    return '${diff.inDays} ngày trước';
  }
}
